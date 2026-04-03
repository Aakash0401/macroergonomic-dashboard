import pytest
import xmlRead

def test_valid_xml():
    """
    Test case to check the validity of XML parsing.

    This test case verifies that the XML parsing function correctly extracts the required information from a valid XML string.
    It checks if the risk score, criticality, and open ports are extracted correctly from the XML string.

    Returns:
        None
    """
    xml_string = """<root><host endtime="1609459200"><ports><port portid="22"/></ports></host></root>"""
    result = xmlRead.get_results_from_string(xml_string, 3)
    assert result['risk_score'] == 25 
    assert result['criticality'] == 0
    assert result['open_ports'] == ['22']


def test_missing_host_tag():
    """
    Test case to check handling of missing host tag.

    This test case verifies that the XML parsing function handles the scenario where the host tag is missing from the XML string.
    It checks if the function returns the expected error message when the host tag is not present.

    Returns:
        None
    """
    xml_string = """<root></root>"""
    result = xmlRead.get_results_from_string(xml_string, 3)
    assert not result['success']
    assert result['message'] == "no host tag"

def test_missing_ports_tag():
    """
    Test case to check handling of missing ports tag.

    This test case verifies that the XML parsing function handles the scenario where the ports tag is missing from the XML string.
    It checks if the function returns the expected error message when the ports tag is not present.

    Returns:
        None
    """
    xml_string = """<root><host endtime="1609459200"></host></root>"""
    result = xmlRead.get_results_from_string(xml_string, 3)
    assert not result['success']
    assert result['message'] == "no ports tag"
