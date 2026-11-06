# ba_meta require api 9
import babase
import bauiv1 as bui
try:
    from bauiv1lib import popup, confirm
except Exception:
    popup = confirm = None
try:
    from bauiv1lib.settings.allsettings import AllSettingsWindow
except Exception:
    AllSettingsWindow = None

import urllib.request
import http.client
import socket
import json
import ssl

import re
import os
import sys
import copy
import asyncio
import pathlib
import hashlib
import contextlib

from typing import override, Any, Dict, List, Optional, Tuple
from datetime import datetime

# Modules used for the BetterParty-style skin
import colorsys
import math
import random
import time

# Modules used for overriding AllSettingsWindow
import logging

PLUGIN_MANAGER_VERSION = "1.1.10"
REPOSITORY_URL = "https://github.com/Taha1389652/Iranian-Plugin-Manager"
CURRENT_TAG = "main"

_env = babase.env()
_app_api_version = babase.app.env.api_version

PLUGIN_ISSUE_TEMPLATE = "plugin-bug-report.yml"
GITHUB_PLUGIN_ISSUE_META = "{repository_url}/issues/new?template={issue_template}"
INDEX_META = "{repository_url}/{content_type}/{tag}/index.json"
CHANGELOG_META = "{repository_url}/{content_type}/{tag}/CHANGELOG.md"
HEADERS = {
    "User-Agent": _env["legacy_user_agent_string"],
}
PLUGIN_DIRECTORY = _env["python_directory_user"]

# compatibility for older API versions.
if _env.get("build_number", 0) < 22714:
    babase._asyncio._g_asyncio_event_loop = babase._asyncio._asyncio_event_loop

loop = babase._asyncio._g_asyncio_event_loop

open_popups = []


def _add_popup(popup):
    open_popups.append(popup)


def _remove_popup(popup):
    try:
        open_popups.remove(popup)
    except ValueError:
        pass


_VERSION_SUFFIX = re.compile(r"[_\-\s]+\d{4,}$")


def _display_name(name):
    """bslife_1457345635  ->  bslife  (پسوند عددی آپلود گیت‌هاب حذف می‌شود)"""
    name = str(name)
    clean = _VERSION_SUFFIX.sub("", name).replace("_", " ").strip()
    return clean or name


def _uiscale(): return bui.app.ui_v1.uiscale
def _regexp_friendly_class_name_shortcut(string): return string.replace(".", "\\.")


def _by_scale(a, b, c):
    u = _uiscale()
    return (
        a if u is babase.UIScale.SMALL else
        b if u is babase.UIScale.MEDIUM else
        c
    )


REGEXP = {
    "plugin_api_version": re.compile(b"(?<=ba_meta require api )(.*)"),
    "plugin_entry_points": re.compile(
        bytes(
            "(ba_meta export (plugin|{})\n+class )(.*)\\(".format(
                _regexp_friendly_class_name_shortcut("babase.Plugin"),
            ),
            "utf-8"
        ),
    ),
    "minigames": re.compile(
        bytes(
            "(ba_meta export ({})\n+class )(.*)\\(".format(
                _regexp_friendly_class_name_shortcut("bascenev1.GameActivity"),
            ),
            "utf-8"
        ),
    ),
}
DISCORD_URL = "https://ballistica.net/discord"


_CACHE = {}


class MD5CheckSumFailed(Exception):
    pass


class PluginNotInstalled(Exception):
    pass


class CategoryDoesNotExist(Exception):
    pass


class NoCompatibleVersion(Exception):
    pass


class PluginSourceNetworkError(Exception):
    pass


class CategoryMetadataParseError(Exception):
    pass


def send_network_request(request):
    return urllib.request.urlopen(request)


async def async_send_network_request(request):
    response = await loop.run_in_executor(None, send_network_request, request)
    return response


def stream_network_response_to_file(request, file, md5sum=None, retries=3):
    response = urllib.request.urlopen(request)
    chunk_size = 16 * 1024
    content = b""
    with open(file, "wb") as fout:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            fout.write(chunk)
            content += chunk
    if md5sum and hashlib.md5(content).hexdigest() != md5sum:
        if retries <= 0:
            raise MD5CheckSumFailed("MD5 checksum match failed.")
        return stream_network_response_to_file(
            request,
            file,
            md5sum=md5sum,
            retries=retries-1,
        )
    return content


async def async_stream_network_response_to_file(request, file, md5sum=None, retries=3):

    content = await loop.run_in_executor(
        None,
        stream_network_response_to_file,
        request,
        file,
        md5sum,
        retries,
    )
    return content


def partial_format(string_template, **kwargs):
    for key, value in kwargs.items():
        string_template = string_template.replace("{" + key + "}", value)
    return string_template


class DNSBlockWorkaround:
    """
    Some ISPs put a DNS block on domains that are needed for plugin manager to
    work properly. This class stores methods to workaround such blocks by adding
    dns.google as a fallback.

    Such as Jio, a pretty popular ISP in India has a DNS block on
    raw.githubusercontent.com (sigh..).

    References:
      * https://github.com/orgs/community/discussions/42655

    Usage:
    -----
    >>> import urllib.request
    >>> import http.client
    >>> import socket
    >>> import ssl
    >>> import json
    >>> DNSBlockWorkaround.apply()
    >>> response = urllib.request.urlopen("https://dnsblockeddomain.com/path/to/resource/")
    """

    _google_dns_cache = {}

    def apply():
        opener = urllib.request.build_opener(
            DNSBlockWorkaround._HTTPHandler,
            DNSBlockWorkaround._HTTPSHandler,
        )
        urllib.request.install_opener(opener)

    def _resolve_using_google_dns(hostname):
        response = urllib.request.urlopen(f"https://dns.google/resolve?name={hostname}")
        response = response.read()
        response = json.loads(response)
        resolved_host = response["Answer"][0]["data"]
        return resolved_host

    def _resolve_using_system_dns(hostname):
        resolved_host = socket.gethostbyname(hostname)
        return resolved_host

    def _resolve_with_workaround(hostname):
        resolved_host_from_cache = DNSBlockWorkaround._google_dns_cache.get(hostname)
        if resolved_host_from_cache:
            return resolved_host_from_cache

        resolved_host_by_system_dns = DNSBlockWorkaround._resolve_using_system_dns(hostname)

        if DNSBlockWorkaround._is_blocked(hostname, resolved_host_by_system_dns):
            resolved_host = DNSBlockWorkaround._resolve_using_google_dns(hostname)
            DNSBlockWorkaround._google_dns_cache[hostname] = resolved_host
        else:
            resolved_host = resolved_host_by_system_dns

        return resolved_host

    def _is_blocked(hostname, address):
        is_blocked = False
        if hostname == "raw.githubusercontent.com":
            # Jio's DNS server may be blocking it.
            is_blocked = address.startswith("49.44.")

        return is_blocked

    class _HTTPConnection(http.client.HTTPConnection):
        def connect(self):
            host = DNSBlockWorkaround._resolve_with_workaround(self.host)
            self.sock = socket.create_connection(
                (host, self.port),
                self.timeout,
            )

    class _HTTPSConnection(http.client.HTTPSConnection):
        def connect(self):
            host = DNSBlockWorkaround._resolve_with_workaround(self.host)
            sock = socket.create_connection(
                (host, self.port),
                self.timeout,
            )
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            sock = context.wrap_socket(sock, server_hostname=self.host)
            self.sock = sock

    class _HTTPHandler(urllib.request.HTTPHandler):
        def http_open(self, req):
            return self.do_open(DNSBlockWorkaround._HTTPConnection, req)

    class _HTTPSHandler(urllib.request.HTTPSHandler):
        def https_open(self, req):
            return self.do_open(DNSBlockWorkaround._HTTPSConnection, req)


class StartupTasks:
    def __init__(self):
        self.plugin_manager = PluginManager()

    def setup_config(self):
        # is_config_updated = False
        existing_plugin_manager_config = copy.deepcopy(
            babase.app.config.get("Community Plugin Manager"))

        plugin_manager_config = babase.app.config.setdefault("Community Plugin Manager", {})
        plugin_manager_config.setdefault("Custom Sources", [])
        installed_plugins = plugin_manager_config.setdefault("Installed Plugins", {})
        for plugin_name in tuple(installed_plugins.keys()):
            plugin = PluginLocal(plugin_name)
            if not plugin.is_installed:
                del installed_plugins[plugin_name]

        # This order is the options will show up in Settings window.
        current_settings = {
            "Auto Update Plugin Manager": True,
            "Auto Update Plugins": True,
            "Auto Enable Plugins After Installation": True,
            "Notify New Plugins": True
        }
        settings = plugin_manager_config.setdefault("Settings", {})

        for setting, value in settings.items():
            if setting in current_settings:
                current_settings[setting] = value

        plugin_manager_config["Settings"] = current_settings

        if plugin_manager_config != existing_plugin_manager_config:
            babase.app.config.commit()

    async def update_plugin_manager(self):
        if not babase.app.config["Community Plugin Manager"]["Settings"]["Auto Update Plugin Manager"]:
            return
        update_details = await self.plugin_manager.get_update_details()
        if update_details:
            to_version, commit_sha = update_details
            bui.screenmessage(f"مدیریت پلاگین در حال به‌روزرسانی به نسخه {to_version}")
            try:
                await self.plugin_manager.update(to_version, commit_sha)
            except MD5CheckSumFailed:
                bui.getsound('error').play()
            else:
                bui.screenmessage("به‌روزرسانی موفقیت‌آمیز بود. برای اعمال تغییرات بازی را مجدداً راه‌اندازی کنید.",
                                  color=(0, 1, 0))
                bui.getsound('shieldUp').play()

    async def update_plugins(self):
        if not babase.app.config["Community Plugin Manager"]["Settings"]["Auto Update Plugins"]:
            return
        await self.plugin_manager.setup_index()
        if "All" not in self.plugin_manager.categories:
            await asyncio.sleep(0.5)
        all_plugins = await self.plugin_manager.categories["All"].get_plugins()
        plugins_to_update = []
        for plugin in all_plugins:
            if plugin.is_installed and await plugin.get_local().is_enabled() and plugin.has_update():
                plugins_to_update.append(plugin.update())
        await asyncio.gather(*plugins_to_update)

    @staticmethod
    def _is_new_supported_plugin(plugin):
        is_an_update = len(plugin.versions) > 1
        if is_an_update:
            return False
        try:
            plugin.latest_compatible_version
        except NoCompatibleVersion:
            return False
        else:
            return True

    async def notify_new_plugins(self):
        if not babase.app.config["Community Plugin Manager"]["Settings"]["Notify New Plugins"]:
            return
        show_max_names = 2
        await self.plugin_manager.setup_index()
        new_num_of_plugins = len(await self.plugin_manager.categories["All"].get_plugins())
        try:
            existing_num_of_plugins = babase.app.config["Community Plugin Manager"]["Existing Number of Plugins"]
        except KeyError:
            babase.app.config["Community Plugin Manager"]["Existing Number of Plugins"] = new_num_of_plugins
            babase.app.config.commit()
            return

        def title_it(plug):
            plug = _display_name(plug)
            return plug
        if existing_num_of_plugins < new_num_of_plugins:
            new_plugin_count = new_num_of_plugins - existing_num_of_plugins
            all_plugins = await self.plugin_manager.categories["All"].get_plugins()
            new_supported_plugins = list(filter(self._is_new_supported_plugin, all_plugins))
            new_supported_plugins.sort(
                key=lambda plugin: plugin.latest_compatible_version.released_on_date,
                reverse=True,
            )
            new_supported_plugins = new_supported_plugins[:new_plugin_count]
            new_supported_plugins_count = len(new_supported_plugins)
            if new_supported_plugins_count > 0:
                new_supported_plugins = ", ".join(map(title_it, (new_supported_plugins
                                                                 if new_supported_plugins_count <= show_max_names else
                                                                 new_supported_plugins[0:show_max_names])
                                                      ))
                if new_supported_plugins_count == 1:
                    notification_text = f"{new_supported_plugins_count} پلاگین جدید ({new_supported_plugins}) در دسترس است!"
                else:
                    notification_text = new_supported_plugins + \
                        ('' if new_supported_plugins_count <= show_max_names else ' و +' +
                         str(new_supported_plugins_count-show_max_names)) + " پلاگین جدید در دسترس است"
                bui.screenmessage(notification_text, color=(0, 1, 0))

        if existing_num_of_plugins != new_num_of_plugins:
            babase.app.config["Community Plugin Manager"]["Existing Number of Plugins"] = new_num_of_plugins
            babase.app.config.commit()

    async def execute(self):
        self.setup_config()
        try:
            # شروع تسک‌های پشت‌زمینه
            asyncio.create_task(self.plugin_manager.clean_removed_plugins())
            asyncio.create_task(self.plugin_manager.check_new_plugins())
            
            await asyncio.gather(
                self.update_plugin_manager(),
                self.update_plugins(),
                self.notify_new_plugins(),
            )
        except urllib.error.URLError:
            pass


class Category:
    def __init__(self, meta_url, tag=CURRENT_TAG):
        self.meta_url = meta_url
        self.tag = tag
        self.request_headers = HEADERS
        self._metadata = _CACHE.get("categories", {}).get(meta_url, {}).get("metadata")
        self._plugins = _CACHE.get("categories", {}).get(meta_url, {}).get("plugins")

    async def fetch_metadata(self):
        if self._metadata is None:
            request = urllib.request.Request(
                self.meta_url.format(content_type="raw", tag=self.tag),
                headers=self.request_headers,
            )
            response = await async_send_network_request(request)
            self._metadata = json.loads(response.read())
            self.set_category_global_cache("metadata", self._metadata)
        return self

    async def validate(self):
        try:
            await self.fetch_metadata()
        except urllib.error.HTTPError as e:
            raise PluginSourceNetworkError(str(e))
        except json.decoder.JSONDecodeError as e:
            raise CategoryMetadataParseError(f"Failed to parse JSON: {str(e)}")
        try:
            await asyncio.gather(
                self.get_name(),
                self.get_description(),
                self.get_plugins_base_url(),
                self.get_plugins(),
            )
        except KeyError:
            raise CategoryMetadataParseError("Failed to parse JSON; missing required fields.")
        else:
            return True

    async def get_name(self):
        await self.fetch_metadata()
        return self._metadata["name"]

    async def get_description(self):
        await self.fetch_metadata()
        return self._metadata["description"]

    async def get_plugins_base_url(self):
        await self.fetch_metadata()
        return self._metadata["plugins_base_url"]

    async def get_plugins(self):
        if self._plugins is None:
            await self.fetch_metadata()
            self._plugins = ([
                Plugin(
                    plugin_info,
                    f"{await self.get_plugins_base_url()}/{plugin_info[0]}.py",
                    tag=self.tag,
                )
                for plugin_info in self._metadata["plugins"].items()
            ])
            self.set_category_global_cache("plugins", self._plugins)
        return self._plugins

    def set_category_global_cache(self, key, value):
        if "categories" not in _CACHE:
            _CACHE["categories"] = {}
        if self.meta_url not in _CACHE["categories"]:
            _CACHE["categories"][self.meta_url] = {}
        _CACHE["categories"][self.meta_url][key] = value

    def unset_category_global_cache(self):
        try:
            del _CACHE["categories"][self.meta_url]
        except KeyError:
            pass

    def cleanup(self):
        self._metadata = None
        self._plugins.clear()
        self.unset_category_global_cache()

    async def refresh(self):
        self.cleanup()
        await self.get_plugins()

    def save(self):
        babase.app.config["Community Plugin Manager"]["Custom Sources"].append(self.meta_url)
        babase.app.config.commit()


class CategoryAll(Category):
    def __init__(self, plugins={}):
        super().__init__(meta_url=None)
        self._name = "All"
        self._description = "All plugins"
        self._plugins = plugins


class PluginLocal:
    def __init__(self, name):
        self.name = name
        self.install_path = os.path.join(PLUGIN_DIRECTORY, f"{name}.py")
        self._entry_point_initials = f"{self.name}."
        self.cleanup()

    def cleanup(self):
        self._content = None
        self._api_version = None
        self._entry_points = []
        self._has_minigames = None

    @property
    def is_installed(self):
        return os.path.isfile(self.install_path)

    @property
    def is_installed_via_plugin_manager(self):
        return self.name in babase.app.config["Community Plugin Manager"]["Installed Plugins"]

    def initialize(self):
        if self.name not in babase.app.config["Community Plugin Manager"]["Installed Plugins"]:
            babase.app.config["Community Plugin Manager"]["Installed Plugins"][self.name] = {}
        return self

    async def uninstall(self):
        if await self.has_minigames():
            self.unload_minigames()
        try:
            os.remove(self.install_path)
        except FileNotFoundError:
            pass
        try:
            del babase.app.config["Community Plugin Manager"]["Installed Plugins"][self.name]
        except KeyError:
            pass
        else:
            self.save()

    @property
    def version(self):
        try:
            version = (babase.app.config["Community Plugin Manager"]
                       ["Installed Plugins"][self.name]["version"])
        except KeyError:
            version = None
        return version

    def _get_content(self):
        with open(self.install_path, "rb") as fin:
            return fin.read()

    def _set_content(self, content):
        with open(self.install_path, "wb") as fout:
            fout.write(content)

    def has_settings(self):
        for plugin_entry_point, plugin_spec in bui.app.plugins.plugin_specs.items():
            if plugin_entry_point.startswith(self._entry_point_initials):
                return plugin_spec.plugin.has_settings_ui()

    def launch_settings(self, source_widget):
        for plugin_entry_point, plugin_spec in bui.app.plugins.plugin_specs.items():
            if plugin_entry_point.startswith(self._entry_point_initials):
                return plugin_spec.plugin.show_settings_ui(source_widget)

    async def get_content(self):
        if self._content is None:
            if not self.is_installed:
                raise PluginNotInstalled("Plugin is not available locally.")
            self._content = await loop.run_in_executor(None, self._get_content)
        return self._content

    async def get_api_version(self):
        if self._api_version is None:
            content = await self.get_content()
            self._api_version = REGEXP["plugin_api_version"].search(content).group()
        return self._api_version

    async def get_entry_points(self):
        if not self._entry_points:
            content = await self.get_content()
            groups = REGEXP["plugin_entry_points"].findall(content)
            entry_points = tuple(f"{self.name}.{group[-1].decode('utf-8')}" for group in groups)
            self._entry_points = entry_points
        return self._entry_points

    async def has_minigames(self):
        if self._has_minigames is None:
            content = await self.get_content()
            self._has_minigames = REGEXP["minigames"].search(content) is not None
        return self._has_minigames

    async def has_plugins(self):
        entry_points = await self.get_entry_points()
        return len(entry_points) > 0

    def load_minigames(self):
        scanner = babase._meta.DirectoryScan(paths="")
        directory, module = self.install_path.rsplit(os.path.sep, 1)
        scanner._scan_module(
            pathlib.Path(directory),
            pathlib.Path(module),
        )
        scanned_results = set(babase.app.meta.scanresults.exports["bascenev1.GameActivity"])
        for game in scanner.results.exports["bascenev1.GameActivity"]:
            if game not in scanned_results:
                bui.screenmessage(f"{game} مینی‌گیم بارگذاری شد")
                babase.app.meta.scanresults.exports["bascenev1.GameActivity"].append(game)

    def unload_minigames(self):
        scanner = babase._meta.DirectoryScan(paths="")
        directory, module = self.install_path.rsplit(os.path.sep, 1)
        scanner._scan_module(
            pathlib.Path(directory),
            pathlib.Path(module),
        )
        new_scanned_results_games = []
        for game in babase.app.meta.scanresults.exports["bascenev1.GameActivity"]:
            if game in scanner.results.exports["bascenev1.GameActivity"]:
                bui.screenmessage(f"{game} مینی‌گیم بارگیری شد")
            else:
                new_scanned_results_games.append(game)
        babase.app.meta.scanresults.exports["bascenev1.GameActivity"] = new_scanned_results_games

    async def is_enabled(self):
        if not await self.has_plugins():
            return True
        for entry_point, plugin_info in babase.app.config["Plugins"].items():
            if entry_point.startswith(self._entry_point_initials) and plugin_info["enabled"]:
                return True
        return False

    async def enable(self):
        for entry_point in await self.get_entry_points():
            if entry_point not in babase.app.config["Plugins"]:
                babase.app.config["Plugins"][entry_point] = {}
            babase.app.config["Plugins"][entry_point]["enabled"] = True
            plugin_spec = bui.app.plugins.plugin_specs.get(entry_point)
            if plugin_spec not in bui.app.plugins.active_plugins:
                self.load_plugin(entry_point)
                bui.screenmessage(f"{entry_point} بارگذاری شد")
        if await self.has_minigames():
            self.load_minigames()
        self.save()

    def load_plugin(self, entry_point):
        plugin_class = babase._general.getclass(entry_point, babase.Plugin)
        loaded_plugin_instance = plugin_class()
        loaded_plugin_instance.on_app_running()

        plugin_spec = babase.PluginSpec(class_path=entry_point, loadable=True)
        plugin_spec.enabled = True
        plugin_spec.plugin = loaded_plugin_instance
        bui.app.plugins.plugin_specs[entry_point] = plugin_spec
        bui.app.plugins.active_plugins.append(plugin_spec.plugin)

    def disable(self):
        for entry_point, plugin_info in babase.app.config["Plugins"].items():
            if entry_point.startswith(self._entry_point_initials):
                plugin_info["enabled"] = False
        self.save()

    def set_version(self, version):
        app = babase.app
        app.config.setdefault("Community Plugin Manager", {})
        app.config["Community Plugin Manager"].setdefault("Installed Plugins", {})
        app.config["Community Plugin Manager"]["Installed Plugins"].setdefault(self.name, {})
        app.config["Community Plugin Manager"]["Installed Plugins"][self.name]["version"] = version
        return self

    async def set_content(self, content):
        if not self._content:
            await loop.run_in_executor(None, self._set_content, content)
            self._content = content
        return self

    async def set_content_from_network_response(self, request, md5sum=None, retries=3):
        if not self._content:
            self._content = await async_stream_network_response_to_file(
                request,
                self.install_path,
                md5sum=md5sum,
                retries=retries,
            )
        return self._content

    def save(self):
        babase.app.config.commit()
        return self


class PluginVersion:
    def __init__(self, plugin, version, tag=CURRENT_TAG):
        self.number, info = version
        self.plugin = plugin
        self.api_version = info["api_version"]
        self.released_on = info["released_on"]
        self.commit_sha = info["commit_sha"]
        self.md5sum = info["md5sum"]

        from urllib.parse import quote
        encoded_name = quote(self.plugin.name, safe='')
        self.download_url = self.plugin.url.format(content_type="raw", tag=tag).replace(self.plugin.name, encoded_name)
        self.view_url = self.plugin.url.format(content_type="blob", tag=tag).replace(self.plugin.name, encoded_name)

    def __eq__(self, plugin_version):
        return (self.number, self.plugin.name) == (plugin_version.number,
                                                   plugin_version.plugin.name)

    def __repr__(self):
        return f"<PluginVersion({self.plugin.name} {self.number})>"

    @property
    def released_on_date(self):
        return datetime.strptime(self.released_on, "%d-%m-%Y")

    async def _download(self, retries=3):
        local_plugin = self.plugin.create_local()
        await local_plugin.set_content_from_network_response(
            self.download_url,
            md5sum=self.md5sum,
            retries=retries,
        )
        local_plugin.set_version(self.number)
        local_plugin.save()
        return local_plugin

    async def install(self, suppress_screenmessage=False):
        try:
            local_plugin = await self._download()
        except MD5CheckSumFailed:
            if not suppress_screenmessage:
                bui.screenmessage(
                    f"{_display_name(self.plugin.name)} بررسی MD5 در هنگام نصب ناموفق بود", color=(1, 0, 0))
            return False
        except Exception as e:
            if not suppress_screenmessage:
                bui.screenmessage(
                    f"{_display_name(self.plugin.name)} خطا در نصب: {str(e)}", color=(1, 0, 0))
            return False
        else:
            if not suppress_screenmessage:
                bui.screenmessage(f"{_display_name(self.plugin.name)} نصب شد", color=(0, 1, 0))
            check = babase.app.config["Community Plugin Manager"]["Settings"]
            if check["Auto Enable Plugins After Installation"]:
                await local_plugin.enable()
            return True


class Plugin:
    def __init__(self, plugin, url, tag=CURRENT_TAG):
        self.name, self.info = plugin
        self.install_path = os.path.join(PLUGIN_DIRECTORY, f"{self.name}.py")
        self.url = url
        self.tag = tag
        self._local_plugin = None

        self._versions = None
        self._latest_version = None
        self._latest_compatible_version = None

    def __repr__(self):
        return f"<Plugin({self.name})>"

    def __str__(self):
        return self.name

    @property
    def view_url(self):
        if self.latest_compatible_version == self.latest_version:
            tag = CURRENT_TAG
        else:
            tag = self.latest_compatible_version.commit_sha
        return self.url.format(content_type="blob", tag=tag)

    @property
    def is_installed(self):
        return os.path.isfile(self.install_path)

    @property
    def versions(self):
        if self._versions is None:
            self._versions = [
                PluginVersion(
                    self,
                    version,
                    tag=self.tag,
                ) for version in self.info["versions"].items()
            ]
        return self._versions

    @property
    def latest_version(self):
        if self._latest_version is None:
            self._latest_version = PluginVersion(
                self,
                tuple(self.info["versions"].items())[0],
                tag=self.tag,
            )
        return self._latest_version

    @property
    def latest_compatible_version(self):
        if self._latest_compatible_version is None:
            for number, info in self.info["versions"].items():
                if info["api_version"] == _app_api_version:
                    self._latest_compatible_version = PluginVersion(
                        self,
                        (number, info),
                        tag=self.tag if self.latest_version.number == number else info["commit_sha"]
                    )
                    break
        if self._latest_compatible_version is None:
            raise NoCompatibleVersion(
                f"{self.name} هیچ نسخه‌ای سازگار با API {_app_api_version} ندارد."
            )
        return self._latest_compatible_version

    def get_local(self):
        if not self.is_installed:
            raise PluginNotInstalled(
                f"{self.name} باید نصب شود تا پلاگین محلی آن دریافت شود.")
        if self._local_plugin is None:
            self._local_plugin = PluginLocal(self.name)
        return self._local_plugin

    def create_local(self):
        return (
            PluginLocal(self.name)
            .initialize()
        )

    async def uninstall(self):
        await self.get_local().uninstall()
        bui.screenmessage(f"{_display_name(self.name)} حذف شد", color=(0.9, 1, 0))

    def has_update(self):
        try:
            latest_compatible_version = self.latest_compatible_version
        except NoCompatibleVersion:
            return False
        else:
            return self.get_local().version != latest_compatible_version.number

    async def update(self):
        if await self.latest_compatible_version.install(suppress_screenmessage=True):
            bui.screenmessage(f"{_display_name(self.name)} به نسخه {self.latest_compatible_version.number} به‌روزرسانی شد",
                              color=(0, 1, 0))
            bui.getsound('shieldUp').play()
        else:
            bui.screenmessage(f"{_display_name(self.name)} بررسی MD5 در هنگام به‌روزرسانی به نسخه "
                              f"{self.latest_compatible_version.number} ناموفق بود",
                              color=(1, 0, 0))
            bui.getsound('error').play()


class PluginManager:
    def __init__(self):
        self.request_headers = HEADERS
        self._index = _CACHE.get("index", {})
        self._changelog = _CACHE.get("changelog", {})
        self.categories = {}
        self.module_path = sys.modules[__name__].__file__
        self._index_setup_in_progress = False
        self._changelog_setup_in_progress = False

    async def get_index(self):
        if not self._index:
            request = urllib.request.Request(
                INDEX_META.format(
                    repository_url=REPOSITORY_URL,
                    content_type="raw",
                    tag=CURRENT_TAG
                ),
                headers=self.request_headers,
            )
            response = await async_send_network_request(request)
            index = json.loads(response.read())
            self.set_index_global_cache(index)
            self._index = index
        return self._index

    async def setup_index(self):
        while self._index_setup_in_progress:
            await asyncio.sleep(0.1)
        self._index_setup_in_progress = not bool(self._index)
        index = await self.get_index()
        await self.setup_plugin_categories(index)
        self._index_setup_in_progress = False

    async def get_changelog(self) -> list[str, bool]:
        requested = False
        if not self._changelog:
            request = urllib.request.Request(CHANGELOG_META.format(
                repository_url=REPOSITORY_URL,
                content_type="raw",
                tag=CURRENT_TAG
            ),
                headers=self.request_headers)
            response = await async_send_network_request(request)
            self._changelog = response.read().decode()
            requested = True
        return [self._changelog, requested]

    async def setup_changelog(self, version=None) -> None:
        if version is None:
            version = PLUGIN_MANAGER_VERSION
        while self._changelog_setup_in_progress:
            await asyncio.sleep(0.1)
        self._changelog_setup_in_progress = not bool(self._changelog)
        try:
            full_changelog = await self.get_changelog()
            if full_changelog[1]:
                pattern = rf"### {version} \(\d\d-\d\d-\d{{4}}\)\n(.*?)(?=### \d+\.\d+\.\d+|\Z)"
                if (len(full_changelog[0].split(version)) > 1):
                    released_on = full_changelog[0].split(version)[1].split('\n')[0]
                    matches = re.findall(pattern, full_changelog[0], re.DOTALL)
                else:
                    matches = None

                if matches:
                    changelog = {
                        'released_on': released_on,
                        'info': matches[0].strip()
                    }
                else:
                    changelog = {'released_on': ' (ارائه نشده)',
                                 'info': f"ورودی تغییرات برای نسخه {version} یافت نشد."}
            else:
                changelog = full_changelog[0]
        except urllib.error.URLError:
            changelog = {'released_on': ' (ارائه نشده)',
                         'info': 'به دلیل مشکلات اینترنتی امکان دریافت تغییرات وجود ندارد.'}
        self.set_changelog_global_cache(changelog)
        self._changelog_setup_in_progress = False

    async def setup_plugin_categories(self, plugin_index):
        self.categories["All"] = None

        requests = []
        for meta_url in plugin_index["categories"]:
            category = Category(meta_url)
            request = category.fetch_metadata()
            requests.append(request)
        for source in babase.app.config["Community Plugin Manager"]["Custom Sources"]:
            source_splits = source.split("@", maxsplit=1)
            if len(source_splits) == 1:
                source_repo, source_tag = source_splits[0], "main"
            else:
                source_repo, source_tag = source_splits
            meta_url = partial_format(
                plugin_index["external_source_url"],
                repository=source_repo,
            )
            category = Category(meta_url, tag=source_tag)
            request = category.fetch_metadata()
            requests.append(request)
        categories = await asyncio.gather(*requests)

        all_plugins = []
        for category in categories:
            self.categories[await category.get_name()] = category
            all_plugins.extend(await category.get_plugins())
        self.categories["All"] = CategoryAll(plugins=all_plugins)

    # ===== پاکسازی خودکار مودهای حذف‌شده (فایل محلی) =====
    async def clean_removed_plugins(self):
        """هر ۱ ثانیه چک می‌کند که آیا مودهای نصب‌شده از روی دیسک حذف شده‌اند"""
        seen_files = set()
        missing_ticks = {}
        while True:
            await asyncio.sleep(1)
            try:
                installed_plugins = babase.app.config.get("Community Plugin Manager", {}).get("Installed Plugins", {})
                removed = []
                silent = []

                for plugin_name in list(installed_plugins.keys()):
                    plugin_path = os.path.join(PLUGIN_DIRECTORY, f"{plugin_name}.py")
                    if os.path.isfile(plugin_path):
                        seen_files.add(plugin_name)
                    elif plugin_name in seen_files:
                        # فایل قبلاً وجود داشته و حالا پاک شده -> واقعاً حذف شده
                        removed.append(plugin_name)
                        seen_files.discard(plugin_name)
                    else:
                        # هنوز فایلی ندیده‌ایم (وسط نصب است یا نصب ناموفق بوده) -> پیام نده
                        # اگر نصب ناموفق شده باشد ورودی ناقص بعد از چند ثانیه بی‌صدا پاک می‌شود
                        missing_ticks[plugin_name] = missing_ticks.get(plugin_name, 0) + 1
                        if missing_ticks[plugin_name] > 120:
                            silent.append(plugin_name)
                            missing_ticks.pop(plugin_name, None)
                for plugin_name in list(missing_ticks):
                    if plugin_name in seen_files or plugin_name not in installed_plugins:
                        missing_ticks.pop(plugin_name, None)
                for name in silent:
                    installed_plugins.pop(name, None)

                if removed:
                    for name in removed:
                        try:
                            del installed_plugins[name]
                            print(f"Plugin {name} removed from config")
                        except Exception:
                            pass
                        bui.screenmessage(f"یک مود از لیست پاک شد: {_display_name(name)}", color=(0.9, 1, 0))
                    if babase.app.config.get("Community Plugin Manager"):
                        babase.app.config.commit()
                        self._reload_main_window()

            except Exception as e:
                print(f"Error in clean_removed_plugins: {e}")

    # ===== دریافت تازه‌ی اسم همه‌ی مودهای لیست (بدون استفاده از کش) =====
    async def _fetch_remote_plugin_names(self):
        """اسم مودهای موجود در ایندکس گیت‌هاب. اگر هر مرحله خطا بدهد None برمی‌گرداند
        تا اشتباهاً مودی «پاک‌شده» حساب نشود."""
        try:
            request = urllib.request.Request(
                INDEX_META.format(repository_url=REPOSITORY_URL, content_type="raw", tag=CURRENT_TAG),
                headers=self.request_headers,
            )
            response = await async_send_network_request(request)
            index = json.loads(response.read())

            sources = [(meta_url, CURRENT_TAG) for meta_url in index["categories"]]
            for source in babase.app.config["Community Plugin Manager"]["Custom Sources"]:
                parts = source.split("@", maxsplit=1)
                repo, tag = (parts[0], "main") if len(parts) == 1 else parts
                sources.append((partial_format(index["external_source_url"], repository=repo), tag))

            names = set()
            for meta_url, tag in sources:
                request = urllib.request.Request(
                    meta_url.format(content_type="raw", tag=tag),
                    headers=self.request_headers,
                )
                response = await async_send_network_request(request)
                metadata = json.loads(response.read())
                names.update(metadata["plugins"].keys())
            return names
        except Exception:
            return None

    # ===== چک کردن مود جدید / مود پاک‌شده از لیست گیت‌هاب =====
    async def check_new_plugins(self):
        """هر ۳۰ ثانیه ایندکس را تازه می‌گیرد و مود جدید / پاک‌شده را اعلام می‌کند"""
        last_plugins = None
        delay = 3
        while True:
            await asyncio.sleep(delay)
            delay = 30
            try:
                current_plugins = await self._fetch_remote_plugin_names()
                if current_plugins is None:
                    continue

                if last_plugins is not None:
                    added = current_plugins - last_plugins
                    removed = last_plugins - current_plugins
                    for name in sorted(added):
                        bui.screenmessage(f"📦 مود جدید: {_display_name(name)}", color=(0, 0.8, 0.3))
                        bui.getsound('cashRegister2').play()
                    for name in sorted(removed):
                        bui.screenmessage(f"یک مود از لیست پاک شد: {_display_name(name)}", color=(1, 0.5, 0.2))
                        bui.getsound('shieldDown').play()
                    if added or removed:
                        # کش قدیمی را بی‌اعتبار کن تا دفعه‌ی بعد لیست تازه خوانده شود
                        _CACHE.pop("index", None)
                        _CACHE.pop("categories", None)
                        self._reload_main_window()

                last_plugins = current_plugins

            except Exception as e:
                print(f"Error in check_new_plugins: {e}")

    def _reload_main_window(self):
        """ریلود پنجره اصلی پلاگین‌منیجر (اگر باز باشد)"""
        try:
            inst = PluginManagerWindow._instance
            if inst is not None and inst.root.exists():
                loop.create_task(inst.refresh())
        except Exception as e:
            print(f"Error reloading window: {e}")

    def cleanup(self):
        for category in self.categories.values():
            if category is not None:
                category.cleanup()
        self.categories.clear()
        self._index.clear()
        self._changelog = None
        self.unset_index_global_cache()

    async def refresh(self):
        self.cleanup()
        await self.setup_index()

    def set_index_global_cache(self, index):
        _CACHE["index"] = index

    def set_changelog_global_cache(self, changelog):
        _CACHE["changelog"] = changelog

    def unset_index_global_cache(self):
        try:
            del _CACHE["index"]
            del _CACHE["changelog"]
        except KeyError:
            pass

    async def get_update_details(self):
        index = await self.get_index()
        for version, info in index["versions"].items():
            if info["api_version"] != _app_api_version:
                continue
            if version == PLUGIN_MANAGER_VERSION:
                return
            else:
                if next(iter(index["versions"])) == version:
                    commit_sha = None
                else:
                    commit_sha = info["commit_sha"]
                return version, commit_sha

    async def update(self, to_version=None, commit_sha=None):
        index = await self.get_index()
        if to_version is None:
            to_version, commit_sha = await self.get_update_details()
        to_version_info = index["versions"][to_version]
        tag = commit_sha or CURRENT_TAG
        download_url = index["plugin_manager_url"].format(
            content_type="raw",
            tag=tag,
        )
        response = await async_send_network_request(download_url)
        content = response.read()
        if hashlib.md5(content).hexdigest() != to_version_info["md5sum"]:
            raise MD5CheckSumFailed("MD5 checksum failed during plugin manager update.")
        with open(self.module_path, "wb") as fout:
            fout.write(content)
        return to_version_info

    async def soft_refresh(self):
        pass




# ═══════════════════════════════════════════════════════════════
# CONSTANTS  (shared look with the BSLIFE Ally manager)
# ═══════════════════════════════════════════════════════════════

_CFG_THEME = 'BetterParty_Theme'
_CFG_FX = 'BetterParty_FX'
_CFG_SPEED = 'BetterParty_Speed'
_FX_T0 = time.time()

TXT = (0.94, 0.96, 1.0)
DIM = (0.72, 0.82, 0.95)
GOLD = (1.0, 0.86, 0.35)
GREEN = (0.5, 1.0, 0.6)
RED = (1.0, 0.5, 0.45)

MyCall = getattr(bui, 'CallPartial', bui.Call)

# SKIN  (rounded cards, themes, FX — from the BetterParty style)
# ═══════════════════════════════════════════════════════════════

THEMES: Dict[str, Dict[str, Any]] = {
    'Aurora': dict(a=(0.16, 0.38, 0.92), b=(0.16, 0.75, 0.35), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Neon Pink': dict(a=(1.0, 0.12, 0.62), b=(0.55, 0.15, 1.0), mode='wave', tex=('heart', 'star', 'circleSoft'), dir=1),
    'Lava': dict(a=(1.0, 0.28, 0.05), b=(0.75, 0.05, 0.12), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Ocean': dict(a=(0.05, 0.40, 0.95), b=(0.02, 0.78, 0.80), mode='wave', tex=('circleOutline', 'circleSoft'), dir=1),
    'Toxic': dict(a=(0.25, 0.95, 0.12), b=(0.75, 0.90, 0.10), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Galaxy': dict(a=(0.40, 0.10, 0.85), b=(0.08, 0.15, 0.55), mode='wave', tex=('star', 'star', 'circleSoft'), dir=1),
    'Candy': dict(a=(1.0, 0.55, 0.80), b=(0.50, 0.80, 1.0), mode='wave', tex=('heart', 'circleSoft'), dir=1),
    'Gold Rush': dict(a=(1.0, 0.78, 0.12), b=(0.95, 0.45, 0.05), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Frost': dict(a=(0.55, 0.85, 1.0), b=(0.85, 0.93, 1.0), mode='wave', tex=('circleSoft', 'star'), dir=-1),
    'Sunset': dict(a=(1.0, 0.35, 0.25), b=(0.65, 0.20, 0.90), mode='wave', tex=('circleSoft', 'star'), dir=1),
    'Matrix': dict(a=(0.05, 0.80, 0.25), b=(0.0, 0.45, 0.15), mode='wave', tex=('circleSoft',), dir=-1),
    'Midnight': dict(a=(0.08, 0.10, 0.30), b=(0.22, 0.12, 0.48), mode='wave', tex=('star', 'circleSoft'), dir=1),
    'Rainbow': dict(a=(1.0, 0.2, 0.2), b=(0.2, 0.2, 1.0), mode='rainbow', tex=('star', 'heart', 'circleSoft'), dir=1),
}
THEME_ORDER = list(THEMES.keys())


def _get_theme(name: str) -> Dict[str, Any]:
    th = THEMES.get(name)
    if th is not None:
        return th
    a, b = THEMES['Aurora']['a'], THEMES['Aurora']['b']
    try:
        saved = babase.app.config.get('PartyWindow_Wave_Colors')
        if (isinstance(saved, (list, tuple)) and len(saved) == 2
                and all(isinstance(c, (list, tuple)) and len(c) == 3 for c in saved)):
            a = tuple(float(x) for x in saved[0])
            b = tuple(float(x) for x in saved[1])
    except Exception:
        pass
    return dict(a=a, b=b, mode='wave', tex=('star', 'circleSoft'), dir=1)


def _theme_rgb(theme, elapsed: float, speed: float = 1.0):
    period = 4.0 / max(0.25, speed)
    if theme.get('mode') == 'rainbow':
        h = (elapsed / (period * 2.5)) % 1.0
        s, v = 0.80, 0.95
    else:
        phase = (elapsed % period) / period
        t = (1 - math.cos(phase * 2 * math.pi)) / 2
        h_a, s_a, v_a = colorsys.rgb_to_hsv(*theme['a'])
        h_b, s_b, v_b = colorsys.rgb_to_hsv(*theme['b'])
        dh = h_b - h_a
        if dh > 0.5:
            dh -= 1.0
        elif dh < -0.5:
            dh += 1.0
        h = (h_a + dh * t) % 1.0
        s = s_a + (s_b - s_a) * t
        v = v_a + (v_b - v_a) * t
    v = min(1.0, v * (0.94 + 0.06 * math.sin(elapsed * 2.3)))
    return colorsys.hsv_to_rgb(h, s, v)


def _accent(rgb, sat: float = 0.55, val: float = 0.88):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return colorsys.hsv_to_rgb(h, min(1.0, 0.25 + s * sat), val)


def _light(rgb, k: float = 0.5):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return colorsys.hsv_to_rgb(h, s * k, 1.0)


def _hsv(h: float, s: float, v: float):
    return colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))


def _palette(rgb) -> Dict[str, Any]:
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    s = min(1.0, 0.15 + s * 0.8)
    return dict(
        body=_hsv(h, s * 0.9, 0.13), card=_hsv(h, s * 0.8, 0.21),
        head=_hsv(h, s * 0.8, 0.29), field=_hsv(h, s * 0.8, 0.10),
        edge=_hsv(h, s * 0.65, 0.72), edge_dim=_hsv(h, s * 0.65, 0.46),
        accent=_accent(rgb), light=_light(rgb, 0.45), text=_light(rgb, 0.16))


def _kind_colors(pal):
    return {'body': (pal['body'], pal['edge']), 'card': (pal['card'], pal['edge_dim']),
            'head': (pal['head'], pal['edge']), 'field': (pal['field'], pal['edge_dim'])}


def _join_color(rgb):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return _hsv(h, 0.35 + s * 0.7, 1.0)


def _danger_color(rgb):
    h, s, _v = colorsys.rgb_to_hsv(*rgb)
    return _hsv(h, 0.3 + s * 0.5, 0.58)


class _RRect:
    def __init__(self, parent, x, y, w, h, r, color=(1, 1, 1)) -> None:
        r = max(1.0, min(r, w / 2.0, h / 2.0))
        white = bui.gettexture('white')
        disc = bui.gettexture('circle')
        self.parts: List[Any] = []

        def add(px, py, pw, ph, tex):
            self.parts.append(bui.imagewidget(
                parent=parent, position=(px, py), size=(pw, ph),
                texture=tex, color=color, opacity=1.0))

        add(x + r, y, w - 2 * r, h, white)
        add(x, y + r, r, h - 2 * r, white)
        add(x + w - r, y + r, r, h - 2 * r, white)
        tile = 2 * r / 0.97
        for cx, cy in ((x + r, y + r), (x + w - r, y + r), (x + r, y + h - r), (x + w - r, y + h - r)):
            add(cx - tile / 2, cy - tile / 2, tile, tile, disc)

    def recolor(self, rgb) -> None:
        for p in self.parts:
            bui.imagewidget(edit=p, color=rgb)


class _Card:
    def __init__(self, parent, x, y, w, h, r, bw: float = 1.6) -> None:
        self.edge = _RRect(parent, x, y, w, h, r)
        self.fill = _RRect(parent, x + bw, y + bw, w - 2 * bw, h - 2 * bw, max(1.0, r - bw))

    def recolor(self, edge, fill) -> None:
        self.edge.recolor(edge)
        self.fill.recolor(fill)


def _rounded_rim(w, h, radius, inset, spacing=18.0):
    rr = max(2.0, radius - inset)
    x0, x1, y0, y1 = inset, w - inset, inset, h - inset
    lh = (x1 - x0) - 2 * rr
    lv = (y1 - y0) - 2 * rr
    arc = math.pi * rr / 2
    total = 2 * lh + 2 * lv + 4 * arc
    n = max(24, int(round(total / spacing)))
    pts = []
    for k in range(n):
        d = total * k / n
        if d < lh:
            p = (x0 + rr + d, y0)
        else:
            d -= lh
            if d < arc:
                a = -math.pi / 2 + d / rr
                p = (x1 - rr + rr * math.cos(a), y0 + rr + rr * math.sin(a))
            else:
                d -= arc
                if d < lv:
                    p = (x1, y0 + rr + d)
                else:
                    d -= lv
                    if d < arc:
                        a = d / rr
                        p = (x1 - rr + rr * math.cos(a), y1 - rr + rr * math.sin(a))
                    else:
                        d -= arc
                        if d < lh:
                            p = (x1 - rr - d, y1)
                        else:
                            d -= lh
                            if d < arc:
                                a = math.pi / 2 + d / rr
                                p = (x0 + rr + rr * math.cos(a), y1 - rr + rr * math.sin(a))
                            else:
                                d -= arc
                                if d < lv:
                                    p = (x0, y1 - rr - d)
                                else:
                                    d -= lv
                                    a = math.pi + d / rr
                                    p = (x0 + rr + rr * math.cos(a), y0 + rr + rr * math.sin(a))
        pts.append((p[0] / w, p[1] / h))
    return pts


class _FXLayer:
    N_PART = 14
    N_ORB = 5
    N_TWINKLE = 16
    N_RING = 3
    N_BURST = 14
    TAIL = 0.20

    def __init__(self, root, width, height, level, theme, halos=None, rim=None) -> None:
        self._w = float(width)
        self._h = float(height)
        self._level = level
        self._theme = theme
        self._n = 0
        self._rnd = random.Random()
        self._last_pulse = -9.0
        w, h = self._w, self._h
        rnd = random.Random(7)
        soft = bui.gettexture('circleSoft')
        star = bui.gettexture('star')

        def img(tex, size=(10, 10)):
            return bui.imagewidget(parent=root, position=(0, 0), size=size, texture=tex,
                                   color=(1, 1, 1), opacity=0.0)

        self._orbs: List[Dict[str, Any]] = []
        for i in range(self.N_ORB):
            self._orbs.append(dict(
                x=rnd.uniform(0.15, 0.85) * w, y=rnd.uniform(0.2, 0.8) * h,
                r=rnd.uniform(50, 100), fx=rnd.uniform(0.12, 0.3),
                fy=rnd.uniform(0.1, 0.25), ph=rnd.uniform(0, 6.28), w=img(soft)))
        self._twk: List[Dict[str, Any]] = []
        for i in range(self.N_TWINKLE):
            self._twk.append(dict(
                x=rnd.uniform(0.06, 0.94) * w, y=rnd.uniform(0.08, 0.92) * h,
                s=rnd.uniform(5, 10), f=rnd.uniform(0.6, 1.8),
                ph=rnd.uniform(0, 6.28), op=-1.0, w=img(star)))

        self._glow = bui.imagewidget(
            parent=root, position=(w * 0.12, h - 80), size=(w * 0.76, 90),
            texture=soft, color=(1, 1, 1), opacity=0.0)
        self._shine = bui.imagewidget(
            parent=root, position=(-80, 6), size=(46, h - 12),
            texture=bui.gettexture('softRectVertical'), color=(1, 1, 1), opacity=0.0)
        self._tshine = bui.imagewidget(
            parent=root, position=(-80, h - 62), size=(30, 46),
            texture=bui.gettexture('softRectVertical'), color=(1, 1, 1), opacity=0.0)
        self._tshine_on = False

        self._halos: List[Dict[str, Any]] = []
        for cx, cy, sz in (halos or []):
            self._halos.append(dict(x=cx, y=cy, s=sz, w=img(soft, (sz, sz))))

        self._dots: List[Dict[str, Any]] = []
        for i, (u, v) in enumerate(rim or []):
            x, y = u * w, v * h
            bloom = None
            if i % 2 == 0:
                bloom = bui.imagewidget(
                    parent=root, position=(x - 9, y - 9), size=(18, 18),
                    texture=soft, color=(1, 1, 1), opacity=0.0)
            self._dots.append(dict(x=x, y=y, op=-1.0, bloom=bloom, w=None))
        for d in self._dots:
            d['w'] = bui.imagewidget(
                parent=root, position=(d['x'] - 3, d['y'] - 3), size=(6, 6),
                texture=soft, color=(1, 1, 1), opacity=0.0)

        self._parts: List[Dict[str, Any]] = []
        for i in range(self.N_PART):
            self._parts.append(dict(
                x=rnd.uniform(0.07, 0.93) * w, speed=rnd.uniform(0.035, 0.10), off=rnd.random(),
                amp=rnd.uniform(4, 18), freq=rnd.uniform(0.6, 1.8), ph=rnd.uniform(0, 6.28),
                size=rnd.uniform(9, 22), maxop=rnd.uniform(0.35, 0.8), tex_i=i, w=img(soft, (12, 12))))

        self._shoot_w = [img(star, (14, 14)), img(soft, (10, 10)), img(soft, (8, 8)), img(soft, (6, 6))]
        self._shoot: Optional[Dict[str, float]] = None
        self._next_shoot = 3.0

        self._rings = [dict(t0=None, x=0.0, y=0.0,
                            w=bui.imagewidget(parent=root, position=(0, 0), size=(20, 20),
                                              texture=bui.gettexture('circleOutline'),
                                              color=(1, 1, 1), opacity=0.0))
                       for _ in range(self.N_RING)]
        self._bursts = [dict(t0=None, x=0.0, y=0.0, vx=0.0, vy=0.0, col=(1, 1, 1),
                             w=img(star if i % 2 else soft, (12, 12)))
                        for i in range(self.N_BURST)]
        self.set_theme(theme)
        self.set_level(level)

    def set_theme(self, theme) -> None:
        self._theme = theme
        texs = theme.get('tex') or ('circleSoft',)
        for p in self._parts:
            try:
                bui.imagewidget(edit=p['w'], texture=bui.gettexture(texs[p['tex_i'] % len(texs)]))
            except Exception:
                pass

    def _hi_widgets(self):
        wl = [o['w'] for o in self._orbs] + [t['w'] for t in self._twk]
        wl += [hh['w'] for hh in self._halos] + list(self._shoot_w)
        wl += [d['bloom'] for d in self._dots if d['bloom'] is not None]
        wl.append(self._tshine)
        return wl

    def _active_count(self) -> int:
        return 0 if self._level <= 0 else (6 if self._level == 1 else self.N_PART)

    def set_level(self, level: int) -> None:
        self._level = level
        hide = []
        if level <= 0:
            hide += self._hi_widgets() + [self._glow, self._shine]
            hide += [p['w'] for p in self._parts] + [d['w'] for d in self._dots]
            hide += [r['w'] for r in self._rings] + [b['w'] for b in self._bursts]
            self._shoot = None
            for r in self._rings:
                r['t0'] = None
            for b in self._bursts:
                b['t0'] = None
        else:
            if level < 2:
                hide += self._hi_widgets()
                self._shoot = None
                self._tshine_on = False
                for b in self._bursts:
                    b['t0'] = None
                hide += [b['w'] for b in self._bursts]
            hide += [p['w'] for p in self._parts[self._active_count():]]
        for d in self._dots:
            d['op'] = -1.0
        for t in self._twk:
            t['op'] = -1.0
        for wd in hide:
            try:
                bui.imagewidget(edit=wd, opacity=0.0)
            except Exception:
                pass

    def pulse(self, x=None, y=None) -> None:
        if self._level <= 0:
            return
        now = time.time() - _FX_T0
        if now - self._last_pulse < 0.35:
            return
        self._last_pulse = now
        ring = min(self._rings, key=lambda r: -1.0 if r['t0'] is None else r['t0'])
        ring.update(t0=now, x=self._w / 2 if x is None else x, y=self._h / 2 if y is None else y)

    def burst(self, x=None, y=None) -> None:
        if self._level < 2:
            return
        now = time.time() - _FX_T0
        cx = self._w / 2 if x is None else x
        cy = self._h * 0.6 if y is None else y
        rnd = self._rnd
        for b in self._bursts:
            a = rnd.uniform(0, 6.283)
            sp = rnd.uniform(70, 200)
            b.update(t0=now, x=cx, y=cy, vx=math.cos(a) * sp, vy=math.sin(a) * sp,
                     col=colorsys.hsv_to_rgb(rnd.random(), 0.55, 1.0))

    def tick(self, elapsed: float, rgb, speed: float) -> None:
        if self._level <= 0:
            return
        self._n += 1
        n = self._n
        w, h = self._w, self._h
        hi = self._level >= 2
        light = _light(rgb, 0.45)
        pulse = (1 + math.sin(elapsed * 1.6 * speed)) / 2

        bui.imagewidget(edit=self._glow, color=light, opacity=0.12 + 0.22 * pulse)
        sx = ((elapsed * 0.13 * speed) % 1.6 - 0.3) * w
        bui.imagewidget(edit=self._shine, position=(sx, 6), opacity=0.07)

        if n % (2 if hi else 3) == 0:
            cnt = len(self._dots)
            base = 0.30 + 0.10 * pulse
            h1 = (elapsed * 0.10 * speed) % 1.0
            h2 = (h1 + 0.5) % 1.0
            recolor = (n % 12 == 0)
            for i, d in enumerate(self._dots):
                t = i / cnt
                k = 0.0
                for head in (h1, h2):
                    dist = (head - t) % 1.0
                    if dist < self.TAIL:
                        k = max(k, (1.0 - dist / self.TAIL) ** 1.6)
                op = base + (0.98 - base) * k
                if k > 0.0 or abs(op - d['op']) > 0.02 or recolor:
                    sz = 6.0 + 5.0 * k
                    col = tuple(c + (1.0 - c) * 0.75 * k for c in light)
                    bui.imagewidget(edit=d['w'], position=(d['x'] - sz / 2, d['y'] - sz / 2),
                                    size=(sz, sz), color=col, opacity=op)
                    if hi and d['bloom'] is not None:
                        bs_ = 16.0 + 16.0 * k
                        bui.imagewidget(edit=d['bloom'],
                                        position=(d['x'] - bs_ / 2, d['y'] - bs_ / 2),
                                        size=(bs_, bs_), color=light, opacity=0.05 + 0.30 * k)
                    d['op'] = op

        direction = self._theme.get('dir', 1)
        span = h - 2 * 17 - 20
        for p in self._parts[:self._active_count()]:
            prog = (p['off'] + elapsed * p['speed'] * speed) % 1.0
            if direction < 0:
                prog = 1.0 - prog
            sz = p['size'] * (0.75 + 0.25 * math.sin(elapsed * 2 + p['ph']))
            x = p['x'] + math.sin(elapsed * p['freq'] + p['ph']) * p['amp']
            y = 17 + 10 + prog * span
            op = math.sin(math.pi * min(1.0, max(0.0, prog))) * p['maxop']
            bui.imagewidget(edit=p['w'], position=(x - sz / 2, y - sz / 2),
                            size=(sz, sz), opacity=op, color=light)

        for r in self._rings:
            if r['t0'] is None:
                continue
            age = elapsed - r['t0']
            if age >= 1.2:
                r['t0'] = None
                bui.imagewidget(edit=r['w'], opacity=0.0)
                continue
            f = age / 1.2
            sz = 30 + f * max(w, h) * 0.95
            bui.imagewidget(edit=r['w'], position=(r['x'] - sz / 2, r['y'] - sz / 2),
                            size=(sz, sz), color=light, opacity=0.65 * (1 - f) ** 1.5)

        if not hi:
            return

        if n % 2 == 0:
            for i, o in enumerate(self._orbs):
                x = o['x'] + math.sin(elapsed * o['fx'] + o['ph']) * 45
                y = o['y'] + math.cos(elapsed * o['fy'] + o['ph']) * 30
                sz = o['r'] * (1 + 0.08 * math.sin(elapsed * 0.9 + o['ph']))
                hh, ss, _vv = colorsys.rgb_to_hsv(*light)
                col = colorsys.hsv_to_rgb((hh + 0.07 * i) % 1.0, min(1.0, ss + 0.3), 1.0)
                bui.imagewidget(edit=o['w'], position=(x - sz / 2, y - sz / 2), size=(sz, sz),
                                color=col,
                                opacity=0.05 + 0.05 * (1 + math.sin(elapsed * 0.6 + o['ph'])) / 2)
            for t in self._twk:
                k = max(0.0, math.sin(elapsed * t['f'] + t['ph'])) ** 3
                op = 0.05 + 0.75 * k
                if abs(op - t['op']) > 0.04:
                    sz = t['s'] * (0.7 + 0.5 * k)
                    bui.imagewidget(edit=t['w'], position=(t['x'] - sz / 2, t['y'] - sz / 2),
                                    size=(sz, sz), color=light, opacity=op)
                    t['op'] = op

        for i, hl in enumerate(self._halos):
            ph = math.sin(elapsed * 2.2 * speed + i * 1.3)
            sz = hl['s'] * (1 + 0.10 * ph)
            bui.imagewidget(edit=hl['w'], position=(hl['x'] - sz / 2, hl['y'] - sz / 2),
                            size=(sz, sz), color=light, opacity=0.10 + 0.14 * (1 + ph) / 2)

        cyc = ((elapsed * speed) % 7.0) / 7.0
        if cyc < 0.22:
            f = cyc / 0.22
            bui.imagewidget(edit=self._tshine, position=(w * 0.2 + f * w * 0.6, h - 62),
                            color=(1, 1, 1), opacity=0.30 * math.sin(math.pi * f))
            self._tshine_on = True
        elif self._tshine_on:
            bui.imagewidget(edit=self._tshine, opacity=0.0)
            self._tshine_on = False

        sh = self._shoot
        if sh is None:
            if elapsed >= self._next_shoot:
                rn = self._rnd
                self._shoot = dict(t0=elapsed, x=rn.uniform(0.08, 0.5) * w, y=rn.uniform(0.7, 0.95) * h,
                                   vx=rn.uniform(260, 340), vy=-rn.uniform(120, 190))
        else:
            age = elapsed - sh['t0']
            if age > 1.0:
                for wd in self._shoot_w:
                    bui.imagewidget(edit=wd, opacity=0.0)
                self._shoot = None
                self._next_shoot = elapsed + self._rnd.uniform(5.0, 10.0)
            else:
                for j, wd in enumerate(self._shoot_w):
                    a = age - 0.05 * j
                    if a < 0:
                        continue
                    x = sh['x'] + sh['vx'] * a
                    y = sh['y'] + sh['vy'] * a
                    sz = (14, 10, 8, 6)[j]
                    bui.imagewidget(edit=wd, position=(x - sz / 2, y - sz / 2), color=light,
                                    opacity=(1 - age) * (0.95, 0.55, 0.35, 0.2)[j])

        for b in self._bursts:
            if b['t0'] is None:
                continue
            age = elapsed - b['t0']
            if age >= 1.1:
                b['t0'] = None
                bui.imagewidget(edit=b['w'], opacity=0.0)
                continue
            x = b['x'] + b['vx'] * age
            y = b['y'] + b['vy'] * age - 70.0 * age * age
            sz = 16 * (1 - 0.4 * age / 1.1)
            bui.imagewidget(edit=b['w'], position=(x - sz / 2, y - sz / 2), size=(sz, sz),
                            color=b['col'], opacity=0.9 * (1 - age / 1.1) ** 1.2)


class _Skin:
    def __init__(self, root, w, h, theme, level, cards, halos=None, radius=18.0) -> None:
        self._items: List[Tuple[_Card, str]] = []
        self._items.append((_Card(root, 0, 0, w, h, radius, bw=2.0), 'body'))
        for x, y, cw, ch, r, kind in cards:
            self._items.append((_Card(root, x, y, cw, ch, r), kind))
        self.fx = _FXLayer(root, w, h, level, theme, halos, rim=_rounded_rim(w, h, radius, 5.0))
        self.pal: Dict[str, Any] = _palette(theme['a'])
        self.recolor(theme['a'])

    def recolor(self, rgb) -> None:
        pal = _palette(rgb)
        self.pal = pal
        kinds = _kind_colors(pal)
        for card, kind in self._items:
            fill, edge = kinds[kind]
            card.recolor(edge, fill)


def _scale() -> float:
    ui = bui.app.ui_v1.uiscale
    return 1.7 if ui is bui.UIScale.SMALL else 1.3 if ui is bui.UIScale.MEDIUM else 1.0


def _win_h() -> int:
    ui = bui.app.ui_v1.uiscale
    return 360 if ui is bui.UIScale.SMALL else 440 if ui is bui.UIScale.MEDIUM else 520


# ═══════════════════════════════════════════════════════════════
# BASE WINDOW
# ═══════════════════════════════════════════════════════════════

_top: Any = None          # the currently open top-level window (login / main / hub)
_api: Any = None
_is_opening = False
_NOSEL = object()


class _Win:
    FX = False

    def __init__(self, W, H, cards, halos=None, outside=False) -> None:
        cfg = babase.app.config
        self.W, self.H = W, H
        self.theme_name = cfg.get(_CFG_THEME, 'Aurora')
        self.theme = _get_theme(self.theme_name)
        self.speed = float(cfg.get(_CFG_SPEED, 1.0))
        lvl = cfg.get(_CFG_FX, 2)
        lvl = lvl if lvl in (0, 1, 2) else 2
        self._btns: List[List[Any]] = []
        self._dcards: List[Tuple[_Card, str]] = []
        self._blend_from: Any = None
        self._blend_t0 = 0.0
        self._n = 0
        ui = bui.app.ui_v1.uiscale
        kw = dict(size=(W, H), transition='in_scale',
                  parent=bui.get_special_widget('overlay_stack'),
                  scale=_scale(), background=False,
                  stack_offset=(0, -10) if ui is bui.UIScale.SMALL else (0, 0))
        if outside:
            kw['on_outside_click_call'] = self.close_sound
        self.root = bui.containerwidget(**kw)
        self.color = _theme_rgb(self.theme, time.time() - _FX_T0, self.speed)
        self.skin = None
        self.fx = None
        self._cards: List[Tuple[_Card, str]] = []
        if self.FX:
            self.skin = _Skin(self.root, W, H, self.theme, lvl, cards, halos)
            self.fx = self.skin.fx
        else:
            self._cards.append((_Card(self.root, 0, 0, W, H, 16, bw=2.0), 'body'))
            for x, y, cw, ch, r, kind in cards:
                self._cards.append((_Card(self.root, x, y, cw, ch, r), kind))
        self.pal = _palette(self.color)
        self._paint(self.color)
        self._timer: Any = bui.AppTimer(
            0.05 if self.FX else 0.2, bui.WeakCallStrict(self._tick), repeat=True)

    # ─── painting ───
    def _paint(self, rgb) -> None:
        if self.skin is not None:
            self.skin.recolor(rgb)
            self.pal = self.skin.pal
        else:
            self.pal = _palette(rgb)
            kinds = _kind_colors(self.pal)
            for card, kind in self._cards:
                fill, edge = kinds[kind]
                card.recolor(edge, fill)
        kinds = _kind_colors(self.pal)
        keep = []
        for card, kind in self._dcards:
            try:
                fill, edge = kinds[kind]
                card.recolor(edge, fill)
                keep.append((card, kind))
            except Exception:
                pass
        self._dcards = keep

    def _kcol(self, kind, rgb):
        pal = self.pal
        if kind == 'active':
            return (1.0, 0.82, 0.25), (0.12, 0.08, 0.0)
        if kind == 'join':
            return _join_color(rgb), (1, 1, 1)
        if kind == 'danger':
            return _danger_color(rgb), pal['text']
        return pal['accent'], pal['text']

    def _accents(self, rgb) -> None:
        keep = []
        for e in self._btns:
            try:
                c, t = self._kcol(e[1], rgb)
                bui.buttonwidget(edit=e[0], color=c, textcolor=t)
                keep.append(e)
            except Exception:
                pass
        self._btns = keep

    def on_tick(self, el: float) -> None:
        t = getattr(self, 'title', None)
        if t is not None:
            try:
                bui.textwidget(edit=t, color=_light(self.color, 0.3), scale=0.95 + 0.03 * math.sin(el * 2.2))
            except Exception:
                pass

    def _tick(self) -> None:
        try:
            if not self.root.exists():
                self._timer = None
                return
            el = time.time() - _FX_T0
            color = _theme_rgb(self.theme, el, self.speed)
            bf = self._blend_from
            if bf is not None:
                k = (time.time() - self._blend_t0) / 1.2
                if k >= 1.0:
                    self._blend_from = None
                else:
                    k = k * k * (3 - 2 * k)
                    color = tuple(bf[i] + (color[i] - bf[i]) * k for i in range(3))
            self.color = color
            self._n += 1
            if self.fx is not None:
                self.fx.tick(el, color, self.speed)
            if self._n % 4 == 0 or not self.FX:
                self._paint(color)
            if self._n % 3 == 0 or not self.FX:
                self._accents(color)
                self.on_tick(el)
        except Exception:
            pass

    # ─── widget helpers ───
    def btn(self, parent, pos, size, label, call, kind='accent', ts=0.8, key=None, **kw):
        c, t = self._kcol(kind, self.color)
        b = bui.buttonwidget(parent=parent, position=pos, size=size, label=label,
                             button_type='square', autoselect=True, color=c, textcolor=t,
                             text_scale=ts, on_activate_call=call, **kw)
        self._btns.append([b, kind, key])
        return b

    def setkind(self, key, kind) -> None:
        for e in self._btns:
            if e[2] == key:
                e[1] = kind

    def lbl(self, parent, pos, text, scale=0.7, color=TXT, h='left', maxwidth=None, v='center'):
        kw = dict(parent=parent, position=pos, size=(0, 0), text=str(text) if text is not None else '',
                  scale=scale, color=color, h_align=h, v_align=v)
        if maxwidth:
            kw['maxwidth'] = maxwidth
        return bui.textwidget(**kw)

    def field(self, parent, pos, size, text='', max_chars=60, desc=''):
        x, y = pos
        w, h = size
        card = _Card(parent, x, y, w, h, 8)
        self._dcards.append((card, 'field'))
        fill, edge = _kind_colors(self.pal)['field']
        card.recolor(edge, fill)
        return bui.textwidget(parent=parent, position=(x + 8, y), size=(w - 16, h), editable=True,
                              text=str(text if text is not None else ''), autoselect=True,
                              h_align='left', v_align='center', maxwidth=w - 24, max_chars=max_chars,
                              description=desc, shadow=0.3, flatness=1.0, color=(1, 1, 1))

    def bar(self, parent, x, y, w, h, me=False):
        return bui.imagewidget(parent=parent, position=(x, y), size=(w, h), texture=bui.gettexture('white'),
                               color=(1, 1, 1) if me else (0, 0, 0), opacity=0.14 if me else 0.30)

    def scroll(self, parent, pos, size, n, row_h):
        sc = bui.scrollwidget(parent=parent, position=pos, size=size, color=(0.4, 0.6, 0.3), border_opacity=0.0)
        hh = max(n * row_h + 6, size[1])
        cont = bui.containerwidget(parent=sc, size=(size[0] - 12, hh), background=False)
        return sc, cont, hh

    # ─── style cycling (shared with BetterParty config) ───
    def cycle_style(self) -> None:
        cfg = babase.app.config
        cur = self.theme_name
        i = (THEME_ORDER.index(cur) + 1) % len(THEME_ORDER) if cur in THEME_ORDER else 0
        name = THEME_ORDER[i]
        self._blend_from = self.color
        self._blend_t0 = time.time()
        self.theme_name = name
        self.theme = _get_theme(name)
        cfg[_CFG_THEME] = name
        try:
            cfg.commit()
        except Exception:
            pass
        if self.fx is not None:
            self.fx.set_theme(self.theme)
            self.fx.pulse()
            self.fx.burst()
        bui.getsound('ding').play()
        bui.screenmessage(f"{L('theme')}: {name}", color=_accent(self.color))

    def close(self) -> None:
        global _top
        _remove_popup(self)
        if _top is self:
            _top = None
        try:
            if self.root and not self.root.transitioning_out:
                bui.containerwidget(edit=self.root, transition='out_scale')
        except Exception:
            pass
        self._timer = None

    def close_sound(self) -> None:
        try:
            bui.getsound('swish').play()
        except Exception:
            pass
        self.close()


class _Dialog(_Win):
    def __init__(self, W, H, title, extra=(), tcolor=None, outside=False) -> None:
        cards = [(12, H - 58, W - 24, 46, 12, 'head')] + list(extra)
        super().__init__(W, H, cards, outside=outside)
        self._tcolor = tcolor
        _add_popup(self)
        self.title = bui.textwidget(parent=self.root, position=(W / 2 + 14, H - 35), size=(0, 0), scale=0.95,
                                    text=str(title), maxwidth=W - 130, h_align='center', v_align='center',
                                    color=tcolor or TXT)
        self.close_btn = self.btn(self.root, (18, H - 52), (38, 38), bui.charstr(bui.SpecialChar.CLOSE),
                                  self.close_sound, ts=0.9)
        bui.containerwidget(edit=self.root, cancel_button=self.close_btn)

    def on_tick(self, el):
        if self._tcolor is None:
            super().on_tick(el)


def _later(delay, call):
    try:
        bui.apptimer(delay, call)
    except Exception:
        call()


# ═══════════════════════════════════════════════════════════════
# UI TEXTS
# ═══════════════════════════════════════════════════════════════

INSTALLED_CATEGORY = "نصب شده"

T_FA = {
    "theme": "تم",
    "style": "ظاهر",
    "settings": "تنظیمات",
    "ok": "باشه",
    "cancel": "انصراف",
    "yes2": "بله",
    "no2": "خیر",
    "empty": "موردی وجود ندارد",
    "ready": "آماده",
    "loading": "در حال بارگذاری...",
    "filter": "فیلتر",
    "refresh": "بازخوانی",
    "all": "همه",
    "custom_sources": "منابع سفارشی",
    "plugins": "پلاگین",
    "version": "نسخه",
    "save": "ذخیره",
    "channels": "Channels",
}

BSRUSH_URL = "https://t.me/bsrush_mod"


def L(key):
    return T_FA.get(key, key)


def _refresh_main_window():
    """بعد از تغییر منابع، لیست پنجره اصلی را دوباره بارگذاری می‌کند."""
    try:
        inst = PluginManagerWindow._instance
        if inst is not None and inst.root.exists():
            loop.create_task(inst.refresh())
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# DIALOGS
# ═══════════════════════════════════════════════════════════════

class ConfirmDialog(_Dialog):
    def __init__(self, title, text, on_yes, danger=True):
        W, H = 400, 200
        super().__init__(W, H, title, extra=[(12, 70, W - 24, H - 140, 12, 'card')],
                         tcolor=RED if danger else GOLD)
        self._on_yes = on_yes
        self.lbl(self.root, (W / 2, H / 2 - 5), text, 0.65, TXT, 'center', maxwidth=W - 50)
        self.btn(self.root, (24, 16), (170, 40), L("yes2"), self._yes, kind='danger' if danger else 'join')
        self.btn(self.root, (W - 194, 16), (170, 40), L("no2"), self.close_sound)

    def _yes(self):
        self.close()
        _later(0.2, MyCall(self._on_yes))


class ChangelogWindow(_Dialog):
    def __init__(self, origin_widget=None):
        W, H = 440, 340
        super().__init__(W, H, 'تغییرات', extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        try:
            released_on = _CACHE['changelog']['released_on']
            logs = _CACHE['changelog']['info'].split('\n')
        except (KeyError, TypeError, AttributeError):
            released_on = ''
            logs = ["امکان بارگذاری تغییرات وجود ندارد"]
        r = self.root
        self.lbl(r, (W / 2, H - 90), PLUGIN_MANAGER_VERSION + released_on, 0.7, GOLD, 'center', W - 60)
        sc, cont, hh = self.scroll(r, (24, 68), (W - 48, H - 170), len(logs), 26)
        rw = W - 48 - 12
        y = hh
        for log_line in logs:
            y -= 26
            self.lbl(cont, (8, y + 13), log_line, 0.6, TXT, maxwidth=rw - 16)
        self.btn(r, (W / 2 - 110, 22), (220, 38), 'مشاهده همه تغییرات', self._open_all, kind='join')

    def _open_all(self):
        bui.getsound('deek').play()
        bui.open_url(REPOSITORY_URL + '/blob/main/CHANGELOG.md')


class AuthorsWindow(_Dialog):
    def __init__(self, authors_info, origin_widget=None):
        W, H = 380, 330
        super().__init__(W, H, 'نویسندگان', extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        rows = []
        for author in authors_info:
            for key, value in author.items():
                if key == 'name':
                    rows.append((str(value), TXT, 0.75))
                else:
                    rows.append((f"{key.title()}: {value if value != '' else 'ارائه نشده'}", DIM, 0.6))
            rows.append(None)
        sc, cont, hh = self.scroll(self.root, (24, 24), (W - 48, H - 110), len(rows), 30)
        rw = W - 48 - 12
        y = hh
        for row in rows:
            y -= 30
            if row is None:
                self.bar(cont, 0, y + 14, rw, 2)
                continue
            self.lbl(cont, (10, y + 15), row[0], row[2], row[1], maxwidth=rw - 20)


class MoreWindow(_Dialog):
    def __init__(self, plugin: 'Plugin', origin=None):
        W, H = 380, 290
        super().__init__(W, H, 'اطلاعات بیشتر', extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        self.plugin = plugin
        last_updated = None
        for value in plugin.info['versions'].values():
            if value['api_version'] == _app_api_version:
                last_updated = value['released_on']
        r = self.root
        rw = W - 48

        def row(label, y):
            self.bar(r, 24, y, rw, 38)
            self.lbl(r, (38, y + 19), label + ":", 0.7, DIM)

        y = H - 70 - 44
        row('نسخه', y)
        self.lbl(r, (W - 38, y + 19), str(plugin.latest_compatible_version.number), 0.75, TXT, 'right', rw / 2)
        y -= 44
        row('آخرین به‌روزرسانی', y)
        self.lbl(r, (W - 38, y + 19), last_updated or 'نامشخص', 0.75, TXT, 'right', rw / 2)
        y -= 44
        row('آدرس منبع', y)
        self.btn(r, (W - 24 - 96, y + 5), (90, 28), 'منبع', MyCall(bui.open_url, plugin.view_url), ts=0.7)
        y -= 44
        row('گزارش باگ', y)
        self.btn(r, (W - 24 - 96, y + 5), (90, 28), 'گزارش', self._open_bug_report_url, ts=0.7)

    def _open_bug_report_url(self):
        import platform
        import urllib.parse
        import baenv

        LOGS_LENGTH_LIMIT = 5000
        _logs = ""
        for entry in baenv._EnvGlobals.get().config.log_handler.get_cached().entries:
            _logs += entry.message + "\n"

        error_logs = f"""```py
{_logs[:LOGS_LENGTH_LIMIT]}
```"""

        params = {
            "title": "[باگ پلاگین]: " + self.plugin.name,
            "plugin-name": self.plugin.name,
            "plugin-version": self.plugin.create_local().version if self.plugin.is_installed else 'نصب نشده',
            "plugin-manager-version": 'v' + PLUGIN_MANAGER_VERSION,
            "bombsquad-version": 'v' + babase.app.env.engine_version + " (" + str(babase.app.env.engine_build_number) + ")",
            "os-version": platform.platform() if platform else babase.app.env.platform.value + babase.app.env.os_version,
            "console-log": error_logs
        }
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        base_url = GITHUB_PLUGIN_ISSUE_META.format(
            repository_url=REPOSITORY_URL, issue_template=PLUGIN_ISSUE_TEMPLATE)
        final_url = f"{base_url}&{query_string}"
        bui.open_url(final_url)


class PluginWindow(_Dialog):
    def __init__(
        self,
        plugin: 'Plugin',
        origin_widget=None,
        plugins_list=None,
        transition='in_scale',
        button_callback=None,
    ):
        async def _noop():
            pass

        self.plugin: Plugin = plugin
        self.plugins_list = plugins_list or [plugin]
        self.button_callback = button_callback or _noop
        self._W, self._H = W, H = 470, 340
        super().__init__(W, H, _display_name(plugin.name),
                         extra=[(12, 70, W - 24, H - 140, 12, 'card')])
        loop.create_task(self.draw_ui())

    def get_description(self, minimum_character_offset=40):
        string = self.plugin.info["description"]
        string_length = len(string)

        partitioned_string = ""
        partitioned_string_length = len(partitioned_string)

        while partitioned_string_length != string_length:
            next_empty_space = string[partitioned_string_length +
                                      minimum_character_offset:].find(" ")
            next_word_end_position = partitioned_string_length + \
                minimum_character_offset + max(0, next_empty_space)
            partitioned_string += string[partitioned_string_length:next_word_end_position]
            if next_empty_space != -1:
                partitioned_string += "\n"
            partitioned_string_length = len(partitioned_string)

        return partitioned_string

    async def draw_ui(self):
        bui.getsound('swish').play()
        W, H = self._W, self._H
        plugin = self.plugin

        # ─── وضعیت پلاگین (قبل از ساخت دکمه‌ها) ───
        actions = []
        to_draw_settings_button = False
        has_update = False
        installed_version = None
        if plugin.is_installed:
            self.local_plugin = plugin.get_local()
            installed_version = self.local_plugin.version
            if await self.local_plugin.has_plugins():
                if await self.local_plugin.is_enabled():
                    actions.append(("غیرفعال", self.disable, 'accent'))
                    if self.local_plugin.has_settings():
                        to_draw_settings_button = True
                else:
                    actions.append(("فعال", self.enable, 'join'))
            actions.append(("حذف", self.uninstall, 'danger'))
            has_update = plugin.has_update()
            if has_update:
                actions.append(("به‌روزرسانی", self.update, 'join'))
        else:
            actions.append(("نصب", self.install, 'join'))

        try:
            if not self.root.exists():
                return
        except Exception:
            return
        r = self.root

        # ─── قبلی / بعدی ───
        i = self.plugins_list.index(plugin) if plugin in self.plugins_list else 0
        self.p_n_plugins = [
            self.plugins_list[i - 1] if (i - 1 > -1) else None,
            self.plugins_list[i + 1] if (i + 1 < len(self.plugins_list)) else None
        ]
        if self.p_n_plugins[0] is not None:
            self.btn(r, (-16, H / 2 - 22), (30, 44), bui.charstr(bui.SpecialChar.LEFT_ARROW),
                     self.show_previous_plugin, ts=1.0, enable_sound=False)
        if self.p_n_plugins[1] is not None:
            self.btn(r, (W - 14, H / 2 - 22), (30, 44), bui.charstr(bui.SpecialChar.RIGHT_ARROW),
                     self.show_next_plugin, ts=1.0, enable_sound=False)

        # ─── نویسنده / توضیحات / نسخه ───
        authors = plugin.info["authors"]
        text = 'توسط ' + ', '.join([author["name"] for author in authors])
        self.btn(r, (24, H - 70 - 30), (W - 48, 26), text,
                 MyCall(AuthorsWindow, authors), ts=0.6)
        self.lbl(r, (W / 2, 188), self.get_description(), 0.6, TXT, 'center', W - 56)
        ver_text = f"{L('version')}: {plugin.latest_compatible_version.number}"
        if installed_version:
            ver_text += f"   |   نصب‌شده: {installed_version}"
        self.lbl(r, (W / 2, 126), ver_text, 0.5, DIM, 'center', W - 56)

        # ─── دکمه‌های کوچک: بیشتر / تنظیمات / آموزش ───
        mini = [("بیشتر...", MyCall(MoreWindow, plugin), 'accent')]
        tutorial_url = plugin.info.get('external_url')
        if to_draw_settings_button:
            mini.append(("تنظیمات", None, 'accent'))
        if tutorial_url:
            mini.append(("آموزش", MyCall(
                ConfirmDialog, 'آموزش', f'این شما را به آدرس زیر می‌برد:\n{tutorial_url}',
                MyCall(bui.open_url, tutorial_url), False), 'accent'))
        gap = 6
        mw = (W - 48 - (len(mini) - 1) * gap) / len(mini)
        x = 24
        for label, call, kind in mini:
            b = self.btn(r, (x, 82), (mw, 26), label, call or (lambda: None), kind=kind, ts=0.65)
            if label == "تنظیمات":
                bui.buttonwidget(edit=b, on_activate_call=MyCall(self.settings, b))
            x += mw + gap

        # ─── دکمه‌های اصلی ───
        n = len(actions)
        gap = 8
        bw = (W - 48 - (n - 1) * gap) / n
        x = 24
        last = None
        for label, call, kind in actions:
            last = self.btn(r, (x, 16), (bw, 40), label, call, kind=kind, ts=0.85)
            x += bw + gap
        if last is not None:
            try:
                bui.containerwidget(edit=r, selected_child=last)
            except Exception:
                pass

    def _ok(self) -> None:
        self.close()

    def button(fn):
        async def asyncio_handler(fn, self, *args, **kwargs):
            await fn(self, *args, **kwargs)
            await self.button_callback()

        def wrapper(self, *args, **kwargs):
            self._ok()

            if asyncio.iscoroutinefunction(fn):
                loop.create_task(asyncio_handler(fn, self, *args, **kwargs))
            else:
                fn(self, *args, **kwargs)
                loop.create_task(self.button_callback())

        return wrapper

    def settings(self, source_widget):
        self.local_plugin.launch_settings(source_widget)

    def show_previous_plugin(self):
        self.close()
        PluginWindow(
            self.p_n_plugins[0],
            None,
            transition='in_left',
            plugins_list=self.plugins_list,
            button_callback=self.button_callback
        )

    def show_next_plugin(self):
        self.close()
        PluginWindow(
            self.p_n_plugins[1],
            None,
            transition='in_right',
            plugins_list=self.plugins_list,
            button_callback=self.button_callback
        )

    @button
    def disable(self) -> None:
        self.local_plugin.disable()

    @button
    async def enable(self) -> None:
        await self.local_plugin.enable()
        bui.getsound('gunCocking').play()

    @button
    async def install(self):
        await self.plugin.latest_compatible_version.install()
        bui.getsound('cashRegister2').play()

    @button
    async def uninstall(self):
        await self.plugin.uninstall()
        bui.getsound('shieldDown').play()

    @button
    async def update(self):
        await self.plugin.update()
        bui.getsound('shieldUp').play()


class PluginCustomSourcesWindow(_Dialog):
    def __init__(self, origin_widget=None):
        W, H = 420, 360
        super().__init__(W, H, 'منابع سفارشی پلاگین',
                         extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        self.selected_source = None
        self._sc = None
        r = self.root
        self._add_source_widget = self.field(r, (24, 22), (W - 48 - 90, 38), '', max_chars=120,
                                             desc='افزودن منبع')
        self.btn(r, (W - 24 - 84, 22), (84, 38), 'افزودن',
                 lambda: loop.create_task(self.add_source()), kind='join')
        self.lbl(r, (W / 2, 72), 'مثال: user/repo@main', 0.5, DIM, 'center', W - 50)
        self.lbl(r, (W / 2, 92), "هشدار: منابع پلاگین شخص ثالث نظارت نمی‌شوند و ممکن است خطرناک باشند!",
                 0.5, RED, 'center', W - 50)
        self.btn(r, (24, 108), (W - 48, 30), 'حذف منبع انتخاب‌شده', self.delete_selected_source,
                 kind='danger', ts=0.7)
        self._list_geo = ((24, 146), (W - 48, H - 70 - 146))
        self.draw_sources()

    def draw_sources(self):
        if self._sc is not None:
            try:
                self._sc.delete()
            except Exception:
                pass
            self._sc = None
        self._btns = [e for e in self._btns if not (isinstance(e[2], str) and e[2].startswith("src:"))]
        sources = list(babase.app.config["Community Plugin Manager"]["Custom Sources"])
        pos, size = self._list_geo
        sc, cont, hh = self.scroll(self.root, pos, size, len(sources), 32)
        self._sc = sc
        rw = size[0] - 12
        y = hh
        for source in sources:
            y -= 32
            self.btn(cont, (0, y + 2), (rw, 28), source, MyCall(self.select_source, source),
                     kind='join' if source == self.selected_source else 'accent', ts=0.65,
                     key="src:" + source)

    def select_source(self, source):
        self.selected_source = source
        for e in self._btns:
            if isinstance(e[2], str) and e[2].startswith("src:"):
                e[1] = 'join' if e[2] == "src:" + source else 'accent'

    async def add_source(self):
        source = (bui.textwidget(query=self._add_source_widget) or '').strip()
        if not source:
            return
        source_splits = source.split("@", maxsplit=1)
        if len(source_splits) == 1:
            source_repo, source_tag = source_splits[0], "main"
        else:
            source_repo, source_tag = source_splits

        pm = PluginManager()
        await pm.setup_index()
        meta_url = partial_format(
            pm._index["external_source_url"],
            repository=source_repo,
        )
        category = Category(meta_url, tag=source_tag)
        try:
            await category.validate()
        except (PluginSourceNetworkError, CategoryMetadataParseError) as e:
            bui.screenmessage(str(e), color=(1, 0, 0))
            bui.getsound('error').play()
            return
        if source in babase.app.config["Community Plugin Manager"]["Custom Sources"]:
            bui.screenmessage("منبع پلاگین قبلاً وجود دارد")
            bui.getsound('error').play()
            return
        babase.app.config["Community Plugin Manager"]["Custom Sources"].append(source)
        babase.app.config.commit()
        bui.screenmessage("منبع پلاگین اضافه شد", color=(0, 1, 0))
        bui.getsound('cashRegister2').play()
        try:
            if self.root.exists():
                self.draw_sources()
        except Exception:
            pass
        _refresh_main_window()

    def delete_selected_source(self):
        if self.selected_source is None:
            return
        try:
            babase.app.config["Community Plugin Manager"]["Custom Sources"].remove(self.selected_source)
        except ValueError:
            return
        babase.app.config.commit()
        bui.screenmessage("منبع پلاگین حذف شد", color=(0.9, 1, 0))
        bui.getsound('shieldDown').play()
        self.selected_source = None
        self.draw_sources()
        _refresh_main_window()


class PluginManagerSettingsWindow(_Dialog):
    LABELS = {
        "Auto Update Plugin Manager": "به‌روزرسانی خودکار مدیریت پلاگین",
        "Auto Update Plugins": "به‌روزرسانی خودکار پلاگین‌ها",
        "Auto Enable Plugins After Installation": "فعال‌سازی خودکار بعد از نصب",
        "Notify New Plugins": "اعلان پلاگین‌های جدید",
    }

    def __init__(self, plugin_manager, origin_widget=None):
        self._plugin_manager = plugin_manager
        self.settings = babase.app.config["Community Plugin Manager"]["Settings"].copy()
        W, H = 430, 370
        super().__init__(W, H, 'تنظیمات', extra=[(12, 12, W - 24, H - 82, 12, 'card')])
        r = self.root
        self._update_button = None
        self._restart_label = None

        # چک‌باکس‌ها
        y = H - 70 - 38
        self.checkboxes = []
        for setting, value in self.settings.items():
            chk = bui.checkboxwidget(
                parent=r, position=(30, y), size=(W - 60, 28),
                text=self.LABELS.get(setting, setting), value=value,
                on_value_change_call=MyCall(self.toggle_setting, setting),
                maxwidth=W - 130, textcolor=TXT, scale=0.8, autoselect=True)
            self.checkboxes.append(chk)
            y -= 30

        self.lbl(r, (W / 2, 150), 'در توسعه پلاگین‌ها یا این مدیریت پلاگین مشارکت کنید!',
                 0.5, TXT, 'center', W - 50)

        # ردیف دکمه‌ها: تغییرات / دیسکورد / گیت‌هاب / آپدیت
        by = 104
        self.btn(r, (24, by), (90, 34), 'تغییرات', self._open_changelog, ts=0.75)
        discord = bui.buttonwidget(
            parent=r, position=(122, by), size=(40, 34), label='', button_type='square',
            autoselect=True, color=(0.525, 0.595, 1.458), on_activate_call=MyCall(bui.open_url, DISCORD_URL))
        bui.imagewidget(parent=r, position=(125, by), size=(34, 34),
                        texture=bui.gettexture("discordLogo"), color=(10 - 0.32, 10 - 0.39, 10 - 0.96),
                        draw_controller=discord)
        github = bui.buttonwidget(
            parent=r, position=(170, by), size=(40, 34), label='', button_type='square',
            autoselect=True, color=(0.23, 0.23, 0.23), on_activate_call=MyCall(bui.open_url, REPOSITORY_URL))
        bui.imagewidget(parent=r, position=(173, by), size=(34, 34),
                        texture=bui.gettexture("githubLogo"), color=(1, 1, 1), draw_controller=github)
        self._update_x = 218
        self._by = by

        self._version_label = self.lbl(r, (W / 2, 84), f'مدیریت پلاگین نسخه {PLUGIN_MANAGER_VERSION}',
                                       0.6, GREEN, 'center', W - 50)
        self.lbl(r, (W / 2, 64), f'نسخه API: {_app_api_version}', 0.5, (0.4, 0.8, 1), 'center', W - 50)

        self.btn(r, (24, 18), (170, 36), L("save"), self.save_settings_button, kind='join')
        self.btn(r, (W - 194, 18), (170, 36), L("cancel"), self.close_sound)

        loop.create_task(self._check_update())

    async def _check_update(self):
        try:
            info = await self._plugin_manager.get_update_details()
        except Exception:
            info = False
        try:
            if not info or not self.root.exists():
                return
        except Exception:
            return
        r = self.root
        W = self.W
        bui.textwidget(edit=self._version_label, color=(1, 0.4, 0.4))
        self._update_button = self.btn(
            r, (self._update_x, self._by), (W - 24 - self._update_x, 34),
            f'به‌روزرسانی به نسخه {info[0]}',
            lambda: loop.create_task(self.update(*info)), kind='join', ts=0.65)
        self._restart_label = self.lbl(r, (W / 2, 124), '', 0.5, GREEN, 'center', W - 50)

    def _open_changelog(self):
        ChangelogWindow()

    def toggle_setting(self, setting, set_value):
        self.settings[setting] = set_value

    def save_settings_button(self):
        babase.app.config["Community Plugin Manager"]["Settings"] = self.settings.copy()
        babase.app.config.commit()
        self.close()
        bui.getsound('gunCocking').play()

    async def update(self, to_version=None, commit_sha=None):
        try:
            await self._plugin_manager.update(to_version, commit_sha)
            await self._plugin_manager.setup_changelog()
        except MD5CheckSumFailed:
            bui.screenmessage("بررسی MD5 در هنگام به‌روزرسانی مدیریت پلاگین ناموفق بود", color=(1, 0, 0))
            bui.getsound('error').play()
        else:
            bui.screenmessage("به‌روزرسانی مدیریت پلاگین موفقیت‌آمیز بود", color=(0, 1, 0))
            bui.getsound('shieldUp').play()
            try:
                bui.textwidget(
                    edit=self._restart_label,
                    text='به‌روزرسانی اعمال شد! برای اعمال تغییرات بازی را مجدداً راه‌اندازی کنید.'
                )
                self._update_button.delete()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW  (same layout as the BSLIFE Ally manager)
# ═══════════════════════════════════════════════════════════════

class PluginManagerWindow(_Win):
    FX = True
    _instance = None

    def __init__(self, transition: str = "in_right", origin_widget: bui.Widget = None):
        old = PluginManagerWindow._instance
        if old is not None:
            try:
                old.close()
            except Exception:
                pass
            PluginManagerWindow._instance = None

        self.plugin_manager = PluginManager()
        self.selected_category = 'All'
        self.selected_alphabet_order = 'a_z'
        self.alphabet_order_selection_button = None
        self._last_filter_text = ""
        self._last_filter_plugins = []
        self._draw_gen = 0
        self._no_internet = False
        self._closing = False
        self._sc = None
        self._empty_lbl = None
        self._row_btns = []
        self._rn = 0
        self.tab_buttons = {}
        self._tab_labels = {}
        self._active_tab = 'All'
        self._view = 'list'

        W, H, P = 620, _win_h(), 10
        hy = H - P - 54
        y0 = P + 34 + 6
        y1 = hy - 8
        ch = y1 - y0
        side_w = 118
        cx = P + side_w + 8
        cw = W - P - cx
        cards = [(P, hy, W - 2 * P, 54, 14, 'head'),
                 (P, y0, side_w, ch, 12, 'card'),
                 (cx, y0, cw, ch, 12, 'card'),
                 (P, P, W - 2 * P, 34, 10, 'head')]
        super().__init__(W, H, cards, halos=[(W - 90, hy + 27, 100), (P + side_w / 2, y0 + ch / 2, 90)])
        PluginManagerWindow._instance = self
        self._geo = (P, y0, ch, side_w)
        self.CW, self.CH = cw - 16, ch - 16
        self._cx, self._cy = cx + 8, y0 + 8
        r = self.root

        close = self.btn(r, (P + 6, hy + 7), (40, 40), bui.charstr(bui.SpecialChar.CLOSE), self.close_sound)
        bui.containerwidget(edit=r, cancel_button=close)
        self.title = self.lbl(r, (W / 2, hy + 37), "مدیریت پلاگین‌های جامعه", 0.95, GOLD, 'center', 300)
        self.head_sub = self.lbl(r, (W / 2, hy + 15), f"{L('version')} {PLUGIN_MANAGER_VERSION}",
                                 0.45, (0.85, 0.93, 1.0), 'center', 300)
        self.btn(r, (W - P - 6 - 74, hy + 9), (74, 36), L("settings"), self._open_settings, ts=0.8)
        self.btn(r, (W - P - 6 - 74 - 8 - 64, hy + 9), (64, 36), L("style"), self.cycle_style, ts=0.8)
        self.status_line = self.lbl(r, (W / 2, P + 17), "", 0.55, DIM, 'center', W - 60)

        # ─── محتوا: نوار جستجو + لیست ───
        CW, CH = self.CW, self.CH
        self.content = bui.containerwidget(parent=r, position=(self._cx, self._cy),
                                           size=(CW, CH), background=False)
        c = self.content
        fw = CW - 46 - 58 - 66 - 12
        self.lbl(c, (4, CH - 23), L("filter") + ":", 0.6, DIM)
        self._filter_widget = self.field(c, (46, CH - 40), (fw, 34), '', max_chars=40, desc=L("filter"))
        self.alphabet_order_selection_button = self.btn(
            c, (46 + fw + 6, CH - 40), (58, 34), 'الف - ز',
            lambda: loop.create_task(self._on_order_button_press()), ts=0.7, enable_sound=False)
        self.btn(c, (CW - 66, CH - 40), (66, 34), L("refresh"),
                 lambda: (bui.getsound('deek').play() or loop.create_task(self.refresh())),
                 ts=0.7, enable_sound=False)
        self._list_h = CH - 48

        # ─── بخش Channels (هم‌اندازه و هم‌جای محتوا؛ فقط یکی در هر زمان دیده می‌شود) ───
        self.channels_box = bui.containerwidget(parent=r, position=(self._cx - 10000, self._cy),
                                                size=(CW, CH), background=False)
        cc = self.channels_box
        self.lbl(cc, (CW / 2, CH - 18), "Channels :", 0.95, GOLD, 'center')
        self.bar(cc, 0, CH - 120, CW, 80)
        bw = min(300, CW - 40)
        self.btn(cc, ((CW - bw) / 2, CH - 104), (bw, 48), u"\u26a1BsRush",
                 MyCall(self._open_link, BSRUSH_URL), kind='join', ts=1.0)

        self._loading_spinner = bui.spinnerwidget(
            parent=r, position=(cx + cw / 2, y0 + ch / 2 - 20), style='bomb', size=48)

        self._render_sidebar()
        self.set_status(L("loading"), DIM)
        loop.create_task(self.draw_index())
        loop.create_task(self.process_search_term())

    # ─── plumbing ───
    def _alive(self):
        try:
            return (not self._closing) and self.root.exists()
        except Exception:
            return False

    def set_status(self, text, color=DIM):
        try:
            bui.textwidget(edit=self.status_line, text=text, color=color)
        except Exception:
            pass

    def close(self):
        self._closing = True
        self._draw_gen += 1
        for p in list(open_popups):
            try:
                p.close()
            except Exception:
                pass
        del open_popups[:]
        if PluginManagerWindow._instance is self:
            PluginManagerWindow._instance = None
        super().close()

    def on_tick(self, el):
        super().on_tick(el)
        self._rn += 1
        if self._rn % 8 == 0 and self._row_btns:
            keep = []
            c, t = self.pal['accent'], self.pal['text']
            for b in self._row_btns:
                try:
                    bui.buttonwidget(edit=b, color=c, textcolor=t)
                    keep.append(b)
                except Exception:
                    pass
            self._row_btns = keep

    def _open_settings(self):
        PluginManagerSettingsWindow(self.plugin_manager)

    def _open_sources(self):
        PluginCustomSourcesWindow()

    def spin(self, show=False):
        w = self._loading_spinner
        p = self.root
        try:
            if w.exists() and p.exists() and not p.transitioning_out:
                bui.spinnerwidget(w, visible=show)
        except Exception:
            pass

    @contextlib.contextmanager
    def exception_handler(self):
        try:
            yield
        except urllib.error.URLError:
            self.spin()
            self._no_internet = True
            self.set_status("مطمئن شوید که به اینترنت متصل هستید و دوباره امتحان کنید.", RED)
            self.plugin_manager._index_setup_in_progress = False
        except RuntimeError:
            pass
        except Exception as e:
            self.spin()
            self.set_status(str(e), RED)
            raise

    # ─── sidebar (categories) ───
    def _render_sidebar(self):
        for b in self.tab_buttons.values():
            try:
                b.delete()
            except Exception:
                pass
        self._btns = [e for e in self._btns if not (isinstance(e[2], str) and e[2].startswith("tab:"))]
        self.tab_buttons = {}
        self._tab_labels = {}
        P, y0, ch, side_w = self._geo
        cats = [k for k in self.plugin_manager.categories.keys() if k != 'All']
        tabs = ['All'] + cats + [INSTALLED_CATEGORY]
        n = len(tabs) + 2
        gap = 3
        th = min(32, (ch - 12 - (n - 1) * gap) / n)
        y = y0 + ch - 6 - th
        for key in tabs:
            base = L("all") if key == 'All' else key
            self._tab_labels[key] = base
            active = key == self._active_tab
            self.tab_buttons[key] = self.btn(
                self.root, (P + 7, y), (side_w - 14, th), ("• " + base) if active else base,
                lambda k=key: loop.create_task(self.select_category(k)),
                kind='active' if active else 'accent', ts=0.8, key="tab:" + key)
            y -= th + gap
        active = self._active_tab == '__channels__'
        self._tab_labels['__channels__'] = L("channels")
        self.tab_buttons['__channels__'] = self.btn(
            self.root, (P + 7, y), (side_w - 14, th), ("• " + L("channels")) if active else L("channels"),
            self.show_channels, kind='active' if active else 'accent', ts=0.8, key="tab:__channels__")
        y -= th + gap
        self.tab_buttons['__sources__'] = self.btn(
            self.root, (P + 7, y), (side_w - 14, th), L("custom_sources"), self._open_sources,
            kind='accent', ts=0.7, key="tab:__sources__")

    def _set_active_tab(self, category):
        """دکمه‌ی بخش فعلی روشن (join) می‌شود و یک • کنارش می‌آید."""
        self._active_tab = category
        for k, b in self.tab_buttons.items():
            if k == '__sources__':
                continue
            active = (k == category)
            self.setkind("tab:" + k, 'active' if active else 'accent')
            base = self._tab_labels.get(k, k)
            try:
                bui.buttonwidget(edit=b, label=("• " + base) if active else base)
            except Exception:
                pass

    def _open_link(self, url):
        try:
            bui.open_url(url)
        except Exception as e:
            bui.screenmessage(str(e), color=(1, 0.3, 0.3))

    def _show_list(self):
        self._view = 'list'
        try:
            bui.containerwidget(edit=self.content, position=(self._cx, self._cy))
            bui.containerwidget(edit=self.channels_box, position=(self._cx - 10000, self._cy))
        except Exception:
            pass

    def show_channels(self):
        if self._closing:
            return
        self._view = 'channels'
        self._set_active_tab('__channels__')
        try:
            bui.containerwidget(edit=self.content, position=(self._cx - 10000, self._cy))
            bui.containerwidget(edit=self.channels_box, position=(self._cx, self._cy))
        except Exception:
            pass
        if self.fx:
            self.fx.pulse()

    # ─── loading ───
    async def draw_index(self):
        self.spin(True)
        with self.exception_handler():
            await self.plugin_manager.setup_changelog()
            await self.plugin_manager.setup_index()
            self._no_internet = False
            self.spin()
            if not self._alive():
                return
            self.set_status(L("ready"), GREEN)
            self._render_sidebar()
            await self.select_category("All")

    async def process_search_term(self):
        while True:
            await asyncio.sleep(0.2)
            try:
                if not self._alive():
                    return
                filter_text = (bui.textwidget(query=self._filter_widget) or '').lower()
                if self.selected_category is None:
                    continue
                await self.draw_plugin_names(self.selected_category, search_term=filter_text,
                                             order=self.selected_alphabet_order)
            except CategoryDoesNotExist:
                pass
            except Exception:
                pass

    async def _on_order_button_press(self):
        bui.getsound('deek').play()
        self.selected_alphabet_order = ('a_z' if self.selected_alphabet_order == 'z_a' else 'z_a')
        try:
            bui.buttonwidget(edit=self.alphabet_order_selection_button,
                             label=('ز - الف' if self.selected_alphabet_order == 'z_a' else 'الف - ز'))
        except Exception:
            pass
        filter_text = (bui.textwidget(query=self._filter_widget) or '').lower()
        if self.plugin_manager.categories != {}:
            if self.plugin_manager.categories['All'] is not None:
                await self.draw_plugin_names(self.selected_category, search_term=filter_text,
                                             refresh=True, order=self.selected_alphabet_order)

    def search_term_filterer(self, plugin, search_term):
        if search_term in plugin.info["description"].lower():
            return True
        if search_term in _display_name(plugin.name).lower():
            return True
        search_term = search_term.replace(" ", "_")
        if search_term in plugin.name:
            return True
        for author in plugin.info["authors"]:
            if search_term in author["name"].lower():
                return True
        return False

    async def _plugin_state(self, plugin):
        """(متن وضعیت، رنگ) برای هر ردیف لیست."""
        try:
            if plugin.is_installed:
                local_plugin = plugin.get_local()
                if await local_plugin.is_enabled():
                    if not local_plugin.is_installed_via_plugin_manager:
                        return "نصب دستی", (0.9, 0.3, 0.3)
                    if local_plugin.version == plugin.latest_compatible_version.number:
                        return "فعال", GREEN
                    return "نیاز به به‌روزرسانی", (1, 0.6, 0)
                return "غیرفعال", DIM
        except Exception:
            pass
        return "نصب نشده", (0.55, 0.55, 0.55)

    async def draw_plugin_names(self, category, search_term="", refresh=False, order='a_z'):
        to_draw_plugin_names = (search_term, category) != (self._last_filter_text, self.selected_category)
        if not (to_draw_plugin_names or refresh):
            return

        try:
            if self.plugin_manager.categories != {}:
                if self.plugin_manager.categories['All'] is not None:
                    category_plugins = await self.plugin_manager.categories[
                        category if category != INSTALLED_CATEGORY else 'All'].get_plugins()
                else:
                    return
            else:
                return
        except (KeyError, AttributeError):
            if self._no_internet:
                return
            raise CategoryDoesNotExist(f"{category} وجود ندارد.")

        if search_term:
            plugins = list(filter(lambda plugin: self.search_term_filterer(plugin, search_term), category_plugins))
        else:
            plugins = list(category_plugins)

        plugins.sort(key=lambda val: _display_name(val.name).lower(), reverse=(order == 'z_a'))

        if plugins == self._last_filter_plugins and not refresh:
            return

        self._last_filter_text = search_term
        self._last_filter_plugins = plugins

        if not self._alive():
            return

        if category == INSTALLED_CATEGORY:
            to_draw = [p for p in plugins if p.is_installed]
        else:
            to_draw = plugins

        ready = []
        for plugin in to_draw:
            try:
                plugin.latest_compatible_version
            except NoCompatibleVersion:
                continue
            ready.append(plugin)

        self._draw_gen += 1
        gen = self._draw_gen
        rows = []
        for plugin in ready:
            text, color = await self._plugin_state(plugin)
            rows.append((plugin, text, color))
        if gen != self._draw_gen or not self._alive():
            return
        self._build_list(rows)

    def _build_list(self, rows):
        c = self.content
        CW = self.CW
        if self._sc is not None:
            try:
                self._sc.delete()
            except Exception:
                pass
            self._sc = None
        if self._empty_lbl is not None:
            try:
                self._empty_lbl.delete()
            except Exception:
                pass
            self._empty_lbl = None
        self._row_btns = []
        try:
            bui.textwidget(edit=self.head_sub,
                           text=f"{len(rows)} {L('plugins')}  |  {L('version')} {PLUGIN_MANAGER_VERSION}")
        except Exception:
            pass
        if not rows:
            self._empty_lbl = self.lbl(c, (CW / 2, self._list_h / 2), L("empty"), 0.8, DIM, 'center')
            return
        sc, cont, hh = self.scroll(c, (0, 0), (CW, self._list_h), len(rows), 32)
        self._sc = sc
        rw = CW - 12
        plugins_list = [p for p, _t, _c in rows]
        y = hh
        accent, tcol = self.pal['accent'], self.pal['text']
        for plugin, text, color in rows:
            y -= 32
            self.bar(cont, 0, y + 2, rw, 28)
            self.lbl(cont, (10, y + 16), _display_name(plugin.name), 0.65, TXT, maxwidth=rw - 190)
            self.lbl(cont, (rw - 64, y + 16), text, 0.5, color, 'right', maxwidth=110)
            b = bui.buttonwidget(parent=cont, position=(rw - 54, y + 5), size=(46, 22), label="...",
                                 button_type='square', autoselect=True, color=accent, textcolor=tcol,
                                 text_scale=0.7,
                                 on_activate_call=MyCall(self.show_plugin_window, plugin, plugins_list))
            self._row_btns.append(b)

    def show_plugin_window(self, plugin, plugins_list, source=None):
        PluginWindow(plugin, None, plugins_list=plugins_list, button_callback=self._after_plugin_action)

    async def _after_plugin_action(self):
        if self._alive():
            await self.draw_plugin_names(self.selected_category, search_term=self._last_filter_text,
                                         refresh=True, order=self.selected_alphabet_order)

    async def select_category(self, category):
        self._show_list()
        self._set_active_tab(category)
        if self.fx:
            self.fx.pulse()
        await self.draw_plugin_names(category, search_term=self._last_filter_text, refresh=True,
                                     order=self.selected_alphabet_order)
        self.selected_category = category

    def cleanup(self):
        self.plugin_manager.cleanup()
        self._draw_gen += 1
        if self._sc is not None:
            try:
                self._sc.delete()
            except Exception:
                pass
            self._sc = None
        self._row_btns = []
        self._last_filter_text = ""
        self._last_filter_plugins = []

    async def refresh(self):
        self.cleanup()
        self.spin(True)
        self.set_status(L("loading"), DIM)
        with self.exception_handler():
            await self.plugin_manager.refresh()
            await self.plugin_manager.setup_changelog()
            await self.plugin_manager.setup_index()
            self._no_internet = False
            self.spin()
            if not self._alive():
                return
            self.set_status(L("ready"), GREEN)
            if self.selected_category not in self.plugin_manager.categories \
                    and self.selected_category != INSTALLED_CATEGORY:
                self.selected_category = 'All'
            was_channels = (self._view == 'channels')
            self._render_sidebar()
            await self.select_category(self.selected_category)
            if was_channels:
                self.show_channels()

    def soft_refresh(self):
        pass




# ═══════════════════════════════════════════════════════════════
# LAUNCHER (برای نسخه‌هایی که AllSettingsWindow قدیمی را ندارند)
# ═══════════════════════════════════════════════════════════════

def _open_plugin_manager():
    try:
        inst = PluginManagerWindow._instance
        if inst is not None and inst.root.exists():
            return
    except Exception:
        pass
    PluginManagerWindow()


def _add_pm_launch_button(win):
    try:
        root = win._root_widget
        if hasattr(win, '_W') and hasattr(win, '_H'):  # BetterParty
            W, H = win._W, win._H
            pos = (W - 10 - 6 - 40 - 8 - 64 - 8 - 40 - 8 - 40, H - 10 - 54 + 9)
            size = (40, 36)
            rgb = _theme_rgb(_get_theme(babase.app.config.get(_CFG_THEME, 'Aurora')), time.time() - _FX_T0, 1.0)
            color, tcol = _accent(rgb), _palette(rgb)['text']
        else:
            width = getattr(win, "_width", 600)
            height = getattr(win, "_height", 500)
            sz = width / 15.0
            pos = (width - width / 30.0, height - 135.0 - sz - 8)
            size = (sz, sz)
            color, tcol = (0.20, 0.45, 0.80), (1.0, 1.0, 1.0)
        bui.buttonwidget(parent=root, size=size, position=pos, label="PM", text_scale=0.8,
                         button_type="square", autoselect=False, color=color, textcolor=tcol,
                         on_activate_call=MyCall(_open_plugin_manager))
    except Exception as e:
        print(f"Plugin manager launcher error: {e}")


def _install_launcher_button():
    """دکمه‌ی «PM» را به پنجره‌ی پارتی اضافه می‌کند (کنار دکمه‌ی مدیریت اتحاد)."""
    try:
        from bauiv1lib import party
    except Exception as e:
        print(f"Plugin manager launcher unavailable: {e}")
        return
    orig = party.PartyWindow
    if isinstance(orig, type):
        orig_init = orig.__init__

        def patched(self, *a, **k):
            orig_init(self, *a, **k)
            _add_pm_launch_button(self)
        orig.__init__ = patched
    else:
        def wrapper(*a, **k):
            win = orig(*a, **k)
            _add_pm_launch_button(win)
            return win
        party.PartyWindow = wrapper

_AllSettingsBase = AllSettingsWindow if AllSettingsWindow is not None else object


class NewAllSettingsWindow(_AllSettingsBase):
    @override
    def main_window_should_preserve_selection(self) -> bool:
        return False

    def __init__(
        self,
        transition: str | None = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale
        width = 1000 if uiscale is bui.UIScale.SMALL else 800
        x_inset = 125 if uiscale is bui.UIScale.SMALL else 105
        height = 490
        top_extra = 20 if uiscale is bui.UIScale.SMALL else 0
        self._plugman_button = None

        super().__init__(transition, origin_widget)

        for child in self._root_widget.get_children():
            child.delete()

        bui.containerwidget(
            edit=self._root_widget, size=(width, height + top_extra)
        )

        if uiscale is bui.UIScale.SMALL:
            self._back_button = None
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self.main_window_back
            )
        else:
            self._back_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(x_inset - 20, height - 85),
                size=(130, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self.main_window_back,
            )
            bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        bui.textwidget(
            parent=self._root_widget,
            position=(0, height - 80),
            size=(width, 25),
            text=bui.Lstr(resource=f'{self._r}.titleText'),
            color=bui.app.ui_v1.title_color,
            h_align='center',
            v_align='center',
            maxwidth=130,
        )

        if self._back_button is not None:
            bui.buttonwidget(
                edit=self._back_button,
                button_type='backSmall',
                size=(60, 60),
                label=bui.charstr(bui.SpecialChar.BACK),
            )

        v = height - 265
        basew = 280 if uiscale is bui.UIScale.SMALL else 230
        baseh = 170
        x_offs = (
            x_inset + (105 if uiscale is bui.UIScale.SMALL else 72) - basew
        )
        x_dif = (basew - 7) / 2
        x_offs2 = x_offs + basew - 7
        x_offs3 = x_offs + 2 * (basew - 7)
        x_offs4 = x_offs + 3 * (basew - 7)
        x_offs5 = x_offs2
        x_offs6 = x_offs3
        x_offs2 -= x_dif
        x_offs3 -= x_dif
        x_offs4 -= x_dif

        def _b_title(
            x: float, y: float, button: bui.Widget, text: str | bui.Lstr
        ) -> None:
            bui.textwidget(
                parent=self._root_widget,
                text=text,
                position=(x + basew * 0.47, y + baseh * 0.22),
                maxwidth=basew * 0.7,
                size=(0, 0),
                h_align='center',
                v_align='center',
                draw_controller=button,
                color=(0.7, 0.9, 0.7, 1.0),
            )

        ctb = self._controllers_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs2, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_controllers,
        )
        if self._back_button is None:
            bbtn = bui.get_special_widget('back_button')
            bui.widget(edit=ctb, left_widget=bbtn)
        _b_title(
            x_offs2, v, ctb, bui.Lstr(resource=f'{self._r}.controllersText')
        )
        imgw = imgh = 130
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs2 + basew * 0.49 - imgw * 0.5, v + 35),
            size=(imgw, imgh),
            texture=bui.gettexture('controllerIcon'),
            draw_controller=ctb,
        )

        gfxb = self._graphics_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs3, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_graphics,
        )
        pbtn = bui.get_special_widget('squad_button')
        bui.widget(edit=gfxb, up_widget=pbtn, right_widget=pbtn)
        _b_title(x_offs3, v, gfxb, bui.Lstr(resource=f'{self._r}.graphicsText'))
        imgw = imgh = 110
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs3 + basew * 0.49 - imgw * 0.5, v + 42),
            size=(imgw, imgh),
            texture=bui.gettexture('graphicsIcon'),
            draw_controller=gfxb,
        )

        abtn = self._audio_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs4, v),
            size=(basew, baseh),
            button_type='square',
            up_widget=pbtn,
            right_widget=pbtn,
            label='',
            on_activate_call=self._do_audio,
        )
        bui.buttonwidget(gfxb, right_widget=abtn)
        _b_title(x_offs4, v, abtn, bui.Lstr(resource=f'{self._r}.audioText'))
        imgw = imgh = 120
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs4 + basew * 0.49 - imgw * 0.5 + 5, v + 35),
            size=(imgw, imgh),
            color=(1, 1, 0),
            texture=bui.gettexture('audioIcon'),
            draw_controller=abtn,
        )

        v -= baseh - 5

        avb = self._advanced_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs5, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_advanced,
        )
        _b_title(x_offs5, v, avb, bui.Lstr(resource=f'{self._r}.advancedText'))
        imgw = imgh = 120
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs5 + basew * 0.49 - imgw * 0.5 + 5, v + 35),
            size=(imgw, imgh),
            color=(0.8, 0.95, 1),
            texture=bui.gettexture('advancedIcon'),
            draw_controller=avb,
        )

        self._plugman_button = pmb = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs6, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            up_widget=abtn,
            on_activate_call=self._do_plugman
        )
        _b_title(x_offs6, v, pmb, bui.Lstr(value="مدیریت پلاگین"))
        imgw = imgh = 120
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs6 + basew * 0.49 - imgw * 0.5 + 5, v + 35),
            size=(imgw, imgh),
            color=(0.8, 0.95, 1),
            texture=bui.gettexture('storeIcon'),
            draw_controller=pmb
        )
        self._restore_state()

    def _do_plugman(self) -> None:
        if not self.main_window_has_control():
            return

        PluginManagerWindow(origin_widget=self._plugman_button)

    def _save_state(self) -> None:
        try:
            sel = self._root_widget.get_selected_child()
            if sel == self._controllers_button:
                sel_name = 'Controllers'
            elif sel == self._graphics_button:
                sel_name = 'Graphics'
            elif sel == self._audio_button:
                sel_name = 'Audio'
            elif sel == self._advanced_button:
                sel_name = 'Advanced'
            elif sel == self._plugman_button:
                sel_name = 'PlugMan'
            elif sel == self._back_button:
                sel_name = 'Back'
            else:
                raise ValueError(f'unrecognized selection \'{sel}\'')
            assert bui.app.classic is not None
            bui.app.ui_v1.window_states[type(self)] = {'sel_name': sel_name}
        except Exception:
            logging.exception('Error saving state for %s.', self)

    def _restore_state(self) -> None:
        try:
            assert bui.app.classic is not None
            sel_name = bui.app.ui_v1.window_states.get(type(self), {}).get(
                'sel_name'
            )
            sel: bui.Widget | None
            if sel_name == 'Controllers':
                sel = self._controllers_button
            elif sel_name == 'Graphics':
                sel = self._graphics_button
            elif sel_name == 'Audio':
                sel = self._audio_button
            elif sel_name == 'Advanced':
                sel = self._advanced_button
            elif sel_name == "PlugMan":
                sel = self._plugman_button
            elif sel_name == 'Back':
                sel = self._back_button
            else:
                sel = self._controllers_button
            if sel is not None:
                bui.containerwidget(edit=self._root_widget, selected_child=sel)
        except Exception:
            logging.exception('Error restoring state for %s.', self)


# ba_meta export babase.Plugin
class EntryPoint(babase.Plugin):
    def on_app_running(self) -> None:
        if AllSettingsWindow is not None:
            from bauiv1lib.settings import allsettings
            allsettings.AllSettingsWindow = NewAllSettingsWindow
        else:
            _install_launcher_button()
        DNSBlockWorkaround.apply()
        asyncio.set_event_loop(babase._asyncio._g_asyncio_event_loop)
        startup_tasks = StartupTasks()

        loop.create_task(startup_tasks.execute())
