# ipaddressモジュールからip_address関数をインポート　https://docs.python.org/ja/3.7/library/ipaddress.html
from ipaddress import ip_address

# ipaddressモジュールの定義属性での判別
def judge_ipattr(ipobj):
    version = ipobj.version
    if ipobj.is_reserved:
        return "Reserved IPv{} Address".format(version)
    elif ipobj.is_loopback:
        return "Loopback IPv{} Address".format(version)
    elif ipobj.is_link_local:
        return "Link Local IPv{} Address".format(version)
    elif ipobj.is_multicast:
        return "Multicast IPv{} Address".format(version)        
    elif ipobj.is_global:
        return "Global IPv{} Address".format(version)
    elif ipobj.is_private:
        return "Private IPv{} Address".format(version)
    elif ipobj.is_unspecified:
        return "Not Defined IPv{} Address".format(version)
    else:
        return "Unexpected IPv{} Address type. Beyond this APi coverage! Search in Google :)".format(version)

# ipaddressモジュールの定義属性での判別
def fetch_ipattr(ipstr):
    if "." in ipstr or ":" in ipstr:
        ipobj = ip_address(ipstr)
        try:
            return judge_ipattr(ipobj)
        except ValueError:
            return  "[Exception] Not IPv4 or IPv6 string format."
    else:
        return "[Error] Not IPv4 or IPv6 string format."