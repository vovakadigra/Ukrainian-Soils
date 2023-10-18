from owslib.wcs import WebCoverageService
import requests

# Define the WCS service URL
wcs_url = "https://io.apps.fao.org/geoserver/ows?service=WCS&version=1.1.1&request=GetCapabilities"

# Connect to the WCS service
wcs = WebCoverageService(wcs_url)

# Specify the coverage identifier (in this case, "GSOCSEQ:socs_u")
coverage_identifier = "GSOCSEQ:socs_u"

# Define the bounding box and CRS you want to request
bbox = (-179.26666667, -179.26666667, 179.9999985582, 82.007747918)
crs = "EPSG:4326"

# Specify the format you want (e.g., "image/tiff", "image/png", or "image/jpeg")
output_format = "image/tiff"

# Make the GetCoverage request
response = wcs.getCoverage(
    identifier=coverage_identifier,
    bbox=bbox,
    crs=crs,
    width=1000,  # Specify the desired width
    height=500,  # Specify the desired height
    format=output_format,
)

# Save the response content to a file
with open("output_data." + output_format.split("/")[-1], "wb") as f:
    f.write(response.read())

print("Data downloaded successfully.")
