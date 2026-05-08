import re

def extract_region_costs(template: str) -> dict:
    """
    Extract region costs from a Jinja2 template.
    
    Args:
        template: The Jinja2 template string
        
    Returns:
        A dictionary mapping region names to their costs
    """
    region_costs = {}
    
    # Find the region cost section
    section_match = re.search(r'workflow\.offloading\.policy\.region\.cost:\s*\n((?:\s+\S+:.*\n?)+)', template)
    
    if not section_match:
        return region_costs
    
    section = section_match.group(1)
    
    # Extract each region and its cost
    for line in section.splitlines():
        match = re.match(r'\s+(\S+):\s*([0-9]*\.?[0-9]+)', line)
        if match:
            region = match.group(1)
            cost = float(match.group(2))
            region_costs[region] = cost
    
    return region_costs


with open("results-20260401T110140/edge-configuration.yaml.j2", "r") as f:
    content = f.read()
    costs = extract_region_costs(content)
    print(costs)
