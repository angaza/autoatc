import sys
import json
import logging
import argparse
import netaddr
import requests

from netaddr import IPAddress

logger = logging.getLogger(__name__)


class ShapingProfile(object):
    def __init__(self, parameters):
        assert "up" in parameters
        assert "down" in parameters

        self._parameters = parameters

    @property
    def parameters(self):
        """Raw dict of shaping parameters."""

        return self._parameters

    @staticmethod
    def from_file(file_, named_format=True):
        """Load shaping profile from a file."""

        parameters = json.load(file_)

        if named_format:
            # the ATC repo profiles have their parameters wrapped
            parameters = parameters["content"]

        return ShapingProfile(parameters)


class ATCAPI(object):
    def __init__(self, host):
        self._host = host
        self._session = requests.Session()

    def _ip_endpoint(self, ip):
        return "http://{}/api/v1/shape/{}/".format(self._host, ip)

    def get_shaping(self, ip):
        """Get the dict of shaping parameters for a given IP."""

        response = self._session.get(self._ip_endpoint(ip))

        if response.status_code == 200:
            return ShapingProfile(response.json())
        elif response.status_code == 404:
            # no shaping is applied to this IP
            return None
        else:
            raise RuntimeError(
                "unexpected response from API",
                response.status_code,
                response.text)

    def set_shaping(self, ip, profile):
        """Set the dict of shaping parameters for a given IP."""

        response = self._session.post(
            self._ip_endpoint(ip),
            json=profile.parameters,
            headers={"X-Real-IP": str(ip)})

        response.raise_for_status()


def refresh_shaping(api, default_profile, ip_min, ip_max, overwrite=False):
    """Loop through IPs, updating shaping to default if none applied."""

    ips = list(netaddr.iter_iprange(ip_min, ip_max, step=1))

    logger.info("applying shaping to %i IPs", len(ips))

    for ip in ips:
        profile = api.get_shaping(ip)

        if overwrite or profile is None:
            logger.info("shaping %s with default profile", ip)

            api.set_shaping(ip, default_profile)
        else:
            logger.debug(
                "profile already set for %s; parameters follow\n%s",
                ip,
                json.dumps(profile.parameters, indent=2))

    logger.debug("shaping applied to %i IPs", len(ips))


def main():
    """Apply default shaping rules to a range of IPs.

    This script is intended to be run periodically against an ATC server,
    probably as a cron job. The script needs to run on a host allowed to set
    the `X-Real-IP` header by the ATC API.
    """

    # ingest command-line arguments
    parser = argparse.ArgumentParser(
        description="Apply a default ATC shaping profile to a range of IPs.")

    parser.add_argument(
        "api_host",
        type=str,
        help="ATC API host, e.g., localhost:8000")
    parser.add_argument(
        "default_profile_path",
        type=str,
        help="path to default profile JSON")
    parser.add_argument(
        "ip_min",
        type=IPAddress,
        help="bottom of the IP range, e.g., 10.0.0.10")
    parser.add_argument(
        "ip_max",
        type=IPAddress,
        help="bottom of the IP range, e.g., 10.0.0.50")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="apply profile even if shaping already in place")
    parser.add_argument(
        "--format",
        choices=["raw", "named"],
        default="named",
        help="format of profile parameters file")
    parser.add_argument(
        "--verbosity",
        metavar="N",
        type=int,
        default=logging.INFO,
        help="logging threshold 0--50; lower is more verbose")

    args = parser.parse_args()

    # set up logging output
    logging.getLogger("requests").setLevel(args.verbosity + 10)

    out_handler = logging.StreamHandler(sys.stdout)

    logging.root.addHandler(out_handler)
    logging.root.setLevel(args.verbosity)

    # apply default profile across the specified IP range
    api = ATCAPI(args.api_host)

    with open(args.default_profile_path, "rt") as default_profile_file:
        default_profile = ShapingProfile.from_file(
            default_profile_file,
            named_format=args.format == "named")

    refresh_shaping(
        api,
        default_profile,
        args.ip_min,
        args.ip_max,
        overwrite=args.overwrite)


if __name__ == "__main__":
    main()
