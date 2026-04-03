import xml.etree.ElementTree as ET


def missing_tag_error(tag_name):
    return {"success": False, "message": f"no {tag_name} tag"}


def get_results(tree, growth_rate):
    """
    Calculate the risk score, criticality, and open ports based on the given XML tree and growth rate.

    Args:
        tree (ElementTree): The XML tree containing the host and port information.
        growth_rate (int): The growth rate used in the risk score calculation.

    Returns:
        dict: A dictionary containing the risk score, criticality, and open ports.

    Raises:
        Exception: If the required tags are missing in the XML tree.

    """
    host = None
    for child in tree:
        if child.tag == "host":
            host = child
    if host is None:
        return missing_tag_error("host")

    end_time = host.attrib["endtime"]

    ports = None
    for child in host:
        if child.tag == "ports":
            ports = child
    if ports is None:
        return missing_tag_error("ports")

    open_ports = []
    for child in ports:
        if child.tag == "port":
            name = "N/A"
            if "portid" in child.attrib:
                name = child.attrib["portid"]
            open_ports.append(name)

    port_count = len(ports)

    # The risk score is based on the number of open ports. As port_count approaches infinity, risk_score approaches 1.
    # This means that the first couple of open ports will give a large increase to the risk score, but later ports count less.
    # The goal is to make sure a potentially infinite number can be represented as a percent.
    # The smaller growth_rate is, the more the earlier ports count.
    # Examples with growth_rate = 3:
    # port_count = 1, risk_score = 0.25; port_count = 2, risk_score = 0.4; port_count = 3, risk_score = 0.5
    # Somewhat based on this: https://www.mathsisfun.com/calculus/limits-infinity.html
    print(port_count, growth_rate)
    risk_score = port_count / (port_count + growth_rate)
    criticality = 0 if risk_score < 1/3 else (1 if risk_score < 2/3 else 2)

    return {"risk_score": round(risk_score * 100), "criticality": criticality, "open_ports": open_ports}


def get_results_from_string(string, growth_rate):
    return get_results(ET.fromstring(string), growth_rate)


if __name__ == "__main__":
    print(get_results(ET.parse("nmapResults.xml").getroot(), 3))
