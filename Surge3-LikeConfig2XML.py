import xml.etree.ElementTree as ET
import xml.dom.minidom

CommentKeywords = ("#", ";", "//")
TypeKeywords = ("[General]", "[Replica]", "[Proxy]", "[Proxy Group]", "[Rule]",
                "[Host]", "[URL Rewrite]", "[Header Rewrite]", "[SSID Setting]", "[MITM]")


def GetGeneralElement(line):
    l = line.split("=")
    element = ET.Element(l[0].replace(" ", ""))
    element.text = l[1].strip()
    return element


def GetReplicaElement(line):
    l = line.split("=")
    element = ET.Element(l[0].replace(" ", ""))
    element.text = l[1].strip()
    return element


def GetProxyElement(line):
    Info_Correspond = ("type", "server", "port")
    l = line.split("=", 1)
    if l[1].find(",") == -1:
        element = ET.Element("Built-in")
        element.set("name", l[0].strip())
        element.set("policy", l[1].strip())
    else:
        element = ET.Element("External")
        element.set("name", l[0].strip())
        info = l[1].split(",")
        for i in range(len(info)):
            if i < 3:
                element.set(Info_Correspond[i], info[i].strip())
            else:
                option = info[i].split("=")
                element.set(option[0].strip(), option[1].strip())
    return element


def GetProxyGroupElement(line):
    l = line.split("=", 1)
    values = l[1].split(",")
    element = ET.Element("policy")
    element.set("name", l[0].strip())
    for i in range(len(values)):
        if i == 0:
            element.set("type", values[i])
        elif values[i].find("=") != -1:
            option = values[i].split("=", 1)
            if option[0].strip() == "policy-path":
                sub = ET.Element("policy-path")
                sub.text = option[1].strip()
                element.append(sub)
            else:
                element.set(option[0].strip(), option[1].strip())
        else:
            sub = ET.Element("policy")
            sub.text = values[i].strip()
            element.append(sub)
    return element


def GetHostElement(line):
    l = line.split("=")
    element = ET.Element("Item")
    element.set("key", l[0].strip())
    element.set("value", l[1].strip())
    return element


def GetRuleElement(line):
    l = line.split(",")
    element = ET.Element(l[0].replace(" ", ""))
    if element.tag == "FINAL":
        element.set("policy", l[1])
        if "dns-failed" in l:
            element.set("dns-failed", "true")
    else:
        element.set("match", l[1])
        element.set("policy", l[2])
    return element


def GetURLRewriteElement(line):
    l = line.split(" ", 3)
    element = ET.Element("Type_"+l[2])
    element.set("type", l[2])
    element.set("regex", l[0])
    element.set("replace", l[1])
    return element


def GetHeaderRewriteElement(line):
    l = line.split(" ", 3)
    element = ET.Element("Type_"+l[1])
    element.set("regex", l[0])
    element.set("field", l[2])
    element.set("value", l[3])
    return element


def GetMITMElement(line):
    l = line.split("=")
    element = ET.Element(l[0].replace(" ", ""))
    element.text = l[1].strip()
    return element


f = open("OKAB3.conf", "r", encoding="utf-8")
root = ET.Element("config")
CurElement = root
for line in f.readlines():
    line = line.strip("\n")
    # 类型关键词
    if line in TypeKeywords:
        line = line.strip("[")
        line = line.strip("]")
        line = line.replace(" ", "")
        root.append(ET.Element(line))
        CurElement = root.find(line)
    # 备注
    elif line.startswith(CommentKeywords):
        temp = ET.Element("comment")
        temp.text = line
        CurElement.append(temp)
    # 排除空行或者只有空白符
    elif line != "" and not line.isspace():
        if CurElement.tag == "General":
            CurElement.append(GetGeneralElement(line))
        elif CurElement.tag == "Replica":
            CurElement.append(GetReplicaElement(line))
        elif CurElement.tag == "Proxy":
            CurElement.append(GetProxyElement(line))
        elif CurElement.tag == "ProxyGroup":
            CurElement.append(GetProxyGroupElement(line))
        elif CurElement.tag == "Rule":
            CurElement.append(GetRuleElement(line))
        elif CurElement.tag == "Host":
            CurElement.append(GetHostElement(line))
        elif CurElement.tag == "URLRewrite":
            CurElement.append(GetURLRewriteElement(line))
        elif CurElement.tag == "HeaderRewrite":
            CurElement.append(GetHeaderRewriteElement(line))
        elif CurElement.tag == "MITM":
            CurElement.append(GetMITMElement(line))

tree = ET.ElementTree(root)
# tree.write("test.xml", xml_declaration="true", encoding="utf-8")
result = xml.dom.minidom.parseString(ET.tostring(tree.getroot())).toprettyxml()
open("Private_Demo.xml", "w", encoding="utf-8").write(result)