# Author: Jim Klo jim.klo[at]sri[dot]com 
#
# LICENSE
# Copyright 2013 SRI International

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from jsonschema import validate, Draft3Validator, ValidationError, validates, RefResolver, _list, _types_msg, FormatChecker
from urllib import urlopen
from lr.lib.uri_validate import URI
import contextlib, json, re, iso8601, urlparse

class UnsupportedFormatError(Exception):
    """
    Valid Draft3 format however unsupported by this validator.
    """

def file_resolver(full_uri):
    '''Used for handling file schemes like: "file:lr/schema/abstract_resource_data.json"'''
    uri, fragment = urlparse.urldefrag(full_uri)
    path = urlparse.urlsplit(uri).path
    try:
        loaded = open(path)
    except:
        loaded = open(re.sub("^/+", "", path))

    return json.load(loaded)


class LRRefResolver(RefResolver):

    @contextlib.contextmanager
    def in_scope(self, scope):

        old_scope = self.resolution_scope
        pieces = urlparse.urlsplit(scope)
        if pieces.scheme == "file":
            self.resolution_scope = ""
        else:
            self.resolution_scope = urlparse.urljoin(old_scope, scope)
        try:
            yield
        finally:
            self.resolution_scope = old_scope



@validates("draft3")
class LRDraft3Validator(Draft3Validator):
    ISO8601_DATE_TIME_REGEX = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})"
        r"(?P<separator>T)(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(?P<timezone>Z)$")

    ISO8601_DATE_TIME_MS_REGEX = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})"
        r"(?P<separator>T)(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(\.(?P<microsecond>[0-9]{1,6}))?(?P<timezone>Z)$")

    ISO8601_DATE_REGEX = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})$")

    # URI regex from https://gist.github.com/138549/download
    URI_REGEX = re.compile("^%s$"%URI, re.X)

    def __init__(self, schema, types=(), resolver=None, format_checker=None):

        if format_checker is None:
            format_checker = FormatChecker()

        if resolver is None:
            resolver = LRRefResolver.from_schema(schema, handlers={"file":file_resolver})

        super(LRDraft3Validator, self).__init__(schema, types, resolver, format_checker)


@FormatChecker.cls_checks("date", ())
def is_date(val):
    m =  LRDraft3Validator.ISO8601_DATE_REGEX.match(val)
    if m:
        groups = m.groupdict()
        try:
            datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]), tzinfo=iso8601.iso8601.UTC)
            return True
        except ValueError:
            pass
    return False

@FormatChecker.cls_checks("date-time", ())
def is_date_time(val):
    m =  LRDraft3Validator.ISO8601_DATE_TIME_REGEX.match(val)
    if m:
        groups = m.groupdict()
        try:
            datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]),
                int(groups["hour"]), int(groups["minute"]), int(groups["second"]),
                tzinfo=iso8601.iso8601.UTC)
            return True
        except ValueError:
            pass
    return False

@FormatChecker.cls_checks("date-time-us")
def is_date_time_us(val):
    m =  LRDraft3Validator.ISO8601_DATE_TIME_MS_REGEX.match(val)
    if m:
        groups = m.groupdict()
        try:
            if groups["microsecond"] is None:
                groups["microsecond"] = 0
            else:
                groups["microsecond"] = int(float("0.%s" % groups["microsecond"]) * 1e6)

            datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]),
                int(groups["hour"]), int(groups["minute"]), int(groups["second"]), int(groups["microsecond"]),
                tzinfo=iso8601.iso8601.UTC)
            return True
        except ValueError:
            pass
    return False

@FormatChecker.cls_checks("utc-millisec")
def is_utc_millisec(val):
    try:
        if val >= 0:
            return True
    except:
        pass

    return False

@FormatChecker.cls_checks("regex")
def is_regex(val):
    try:
        exp = re.compile(val)
        if exp:
            return True
    except:
        pass
    return False

@FormatChecker.cls_checks("uri")
def is_uri(val):
    if LRDraft3Validator.URI_REGEX.match(val) is not None:
        # print "regex matched a uri: %r" % val
        return True

def unsupported(val):
    raise UnsupportedFormatError()

FormatChecker.cls_checks("time", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("color", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("style", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("phone", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("email", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("ip-address", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("ipv6", UnsupportedFormatError)(unsupported)
FormatChecker.cls_checks("hostname", UnsupportedFormatError)(unsupported)




LRDraft3Validator.META_SCHEMA = Draft3Validator.META_SCHEMA
LRDraft3Validator.META_SCHEMA["properties"]["format"].update(
    {
        "type": "string",
        "enum": ["date-time", "date-time-us", "date", "utc-millisec", "regex", "uri"]
    }
)           



