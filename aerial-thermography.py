import datetime as dt
from jinja2 import Template
from weasyprint import HTML
import os
import pandas as pd
import yaml
import boto3
import logging
import argparse
from utils.config import AppConfig

logging.basicConfig(level=logging.INFO)

# Create a logger
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

config_file = "config.yaml"

#aws variables
bucket_name=None
csv_file_name=None
thermal_image_file=None
RGB_image_file=None

#local path variables
csv_file_name_local=None
thermal_image_file_local=None
RGB_image_file_local=None


# Define other directory paths relative to ROOT
ROOT = os.getcwd()
ASSETS_DIR = os.path.join(ROOT, 'assets')
TEMPLAT_SRC = os.path.join(ROOT, 'templates')
CSS_SRC = os.path.join(ROOT, 'static')
DEST_DIR =os.path.join(ROOT, 'output')
DEST_HTML=os.path.join(ROOT,'HTML_Final')
IMG_SRC=os.path.join(ROOT,'Thermal_image')
CSV_SRC=os.path.join(ROOT,'CSV')


# HTML_DIR=os.path.join(ROOT,'HTML_Final')

TEMPLATE = 'template.html'
OUTPUT_FILENAME = 'my-report.pdf'
todayStr = dt.datetime.now().strftime("%d/%m/%Y")
OUTPUT_HTML='index.html'
CSV_FILENAME_Thermal='thermal.csv'
CSV_FILENAME_RGB='rgb.csv'

# to fetch image from and csv files from aws
class AWSConfigurator:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.configure_aws()

    def load_config(self, config_file):
        config_path = os.path.join('config', config_file)
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def configure_aws(self):
        self.aws_session = boto3.Session(
            region_name=self.config['aws_region'],
            aws_access_key_id=self.config['aws_access_key_id'],
            aws_secret_access_key=self.config['aws_secret_access_key']
        )
        # Create an S3 client once during configuration
        self.s3_client = self.aws_session.client('s3')
    
    def download_csv_from_s3(self, bucket_name, object_key):
        try:
            # Download the CSV file from S3 to a temporary file
                temp_file_path=os.path.join(CSV_SRC,CSV_FILENAME)
                with open(temp_file_path, 'wb') as temp_file:
                    self.s3_client.download_fileobj(bucket_name, object_key, temp_file)
                    logger.info("CSV file downloaded successfully from S3.")
                    return temp_file
        except Exception as e:
            logger.error(f"Error downloading CSV file from S3: {e}")
            return None


def start():
    #data fetched from defect details list.
    data = {
    0: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T67',
        'Module No.': '(10, 6)',
        'Minimum Temp.(°C)': 28.88999939,
        'Maximum Temp.(°C)': 41.86999893,
        'Average Temp.(°C)': 37.9,
        'Delta(Δ) Temp.(°C)': -15.51378,
        'Latitude': '28.43509',
        'Longitude': '28.43509'
    },
    1: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T24',
        'Module No.': '(12, 15)',
        'Minimum Temp.(°C)': 33.72000122,
        'Maximum Temp.(°C)': 52.54999924,
        'Average Temp.(°C)': 43.41,
        'Delta(Δ) Temp.(°C)': -15.51413,
        'Latitude': '28.43605',
        'Longitude': '28.43605'
    },
    2: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T24',
        'Module No.': '(7, 15)',
        'Minimum Temp.(°C)': 24.87000084,
        'Maximum Temp.(°C)': 51.29999924,
        'Average Temp.(°C)': 44.96,
        'Delta(Δ) Temp.(°C)': -15.51410,
        'Latitude': '28.43605',
        'Longitude': '28.43605'
    },
    3: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T11',
        'Module No.': '(11, 13)',
        'Minimum Temp.(°C)': 33.70999908,
        'Maximum Temp.(°C)': 43.90000153,
        'Average Temp.(°C)': 40.01,
        'Delta(Δ) Temp.(°C)': -15.51422,
        'Latitude': '28.43431',
        'Longitude': '28.43431'
    },
    4: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T11',
        'Module No.': '(11, 15)',
        'Minimum Temp.(°C)': 28.81999969,
        'Maximum Temp.(°C)': 43.61999893,
        'Average Temp.(°C)': 39.17,
        'Delta(Δ) Temp.(°C)': -15.51422,
        'Latitude': '28.43434',
        'Longitude': '28.43434'
    },
    5: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T11',
        'Module No.': '(4, 15)',
        'Minimum Temp.(°C)': 36.11999893,
        'Maximum Temp.(°C)': 46.54000092,
        'Average Temp.(°C)': 42.34,
        'Delta(Δ) Temp.(°C)': -15.51418,
        'Latitude': '28.43434',
        'Longitude': '28.43434'
    },
    6: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T11',
        'Module No.': '(8, 6)',
        'Minimum Temp.(°C)': 30.45999908,
        'Maximum Temp.(°C)': 46.95000076,
        'Average Temp.(°C)': 43.08,
        'Delta(Δ) Temp.(°C)': -15.51420,
        'Latitude': '28.43424',
        'Longitude': '28.43424'
    },
    7: {
        'Defect': 'Broken_Glass',
        'Block No.': 'BLOCK-1',
        'Table No.': 'B1/T11',
        'Module No.': '(7, 6)',
        'Minimum Temp.(°C)': 30.97999954,
        'Maximum Temp.(°C)': 46.86000061,
        'Average Temp.(°C)': 42.91,
        'Delta(Δ) Temp.(°C)': -15.51420,
        'Latitude': '28.43424',
        'Longitude': '28.43424'
    }
}
    #dictionary to map modules no to imagefilename
    module_filename_dict = {}
    
    #reading csv file from aws
    aws_configurator = AWSConfigurator(config_file)

    # csv_object_key = f"{bucket_location}/{csv_file_name}"
    csv_file_path = aws_configurator.download_csv_from_s3(bucket_name, 'demoproject/csv/RGB_CSV1.csv',os.path.join(CSV_SRC,CSV_FILENAME_Thermal))
    csv_file_path2= aws_configurator.download_csv_from_s3(bucket_name, 'demoproject/csv/Thermal_Image.csv',os.path.join(CSV_SRC,CSV_FILENAME_RGB))
    if csv_file_path:
        file_to_read=os.path.join(CSV_SRC,CSV_FILENAME_Thermal)
        with open(file_to_read, 'r') as csv_file:
            csv_reader = pd.read_csv(csv_file)
            for  index, row in csv_reader.iterrows():
                module_no = row['Module No.']
                table_no= row['Table No.']
                block_no= row['Block No.']
                defect_name=row['Defect']
                RGB_csv =  row['filename']
                search_key=f"{module_no}+{table_no}+{block_no}+{defect_name}"
                module_filename_dict[search_key] = [RGB_csv]
     
    if csv_file_path2:
        file_to_read=os.path.join(CSV_SRC,CSV_FILENAME_RGB)
        with open(file_to_read, 'r') as csv_file:
            csv_reader = pd.read_csv(csv_file)
            for  index, row in csv_reader.iterrows():
                module_no = row['Module No.']
                table_no= row['Table No.']
                block_no= row['Block No.']
                Thermal_csv= row['filename']
                defect_name=row['Defect']
                search_key=f"{module_no}+{table_no}+{block_no}+{defect_name}"
                if search_key in module_filename_dict:
                    if len(module_filename_dict[search_key]) < 2:
                        module_filename_dict[search_key].append(Thermal_csv)
                    else:
                        module_filename_dict[search_key][1] = Thermal_csv
                else:
                    module_filename_dict[search_key] = [Thermal_csv]
        print(module_filename_dict)
        
        # Retrieving thermal image url and RGB image url for each image name in aws and inserting back to dictionary.
        for module_no, filename in module_filename_dict.items():
            RGB_csv, Thermal_csv = filename  # Unpack the list into separate variables
            object_key_RGB = f"{RGB_image_file}/{RGB_csv}"
            object_key_thermal = f"{thermal_image_file}/{Thermal_csv}"
            #getting url for reading image from aws bucket
            presigned_url_thermal = object_key_RGB
            presigned_url_RGB=object_key_thermal
            
            if presigned_url_thermal:
                thermal_url = presigned_url_thermal
            else:
                logger.error(f"Failed to generate presigned URL for {filename}")
            if presigned_url_RGB:
               RGB_url=presigned_url_RGB
            else:
                logger.error(f"Failed to generate presigned URL for {filename}")
            
            module_filename_dict[module_no] = [thermal_url, RGB_url]

    else :
        logger.error("Failed to retrieve CSV file from S3.")

   
    #reading csv file from local storage if not found on aws s3
    if not csv_file_path2 or csv_file_path:
        module_filename_dict = {}
        csv_path=csv_file_name_1_local
        if csv_path:
            with open(csv_path, "r") as file:
                csv_file = pd.read_csv(file)
                for  index, row in csv_file.iterrows():
                    module_no = row['Module No.']
                    table_no= row['Table No.']
                    block_no= row['Block No.']
                    defect_name=row['Defect']
                    RGB_csv =  row['filename']
                    search_key=f"{module_no}+{table_no}+{block_no}+{defect_name}"
                    module_filename_dict[search_key] = [RGB_csv]
     
        csv_path=csv_file_name_2_local
        if csv_path:
            with open(csv_path, 'r') as csv_file:
                csv_path = pd.read_csv(csv_file)
                for  index, row in csv_reader.iterrows():
                    module_no = row['Module No.']
                    table_no= row['Table No.']
                    block_no= row['Block No.']
                    Thermal_csv= row['filename']
                    defect_name=row['Defect']
                    search_key=f"{module_no}+{table_no}+{block_no}+{defect_name}"
                    if search_key in module_filename_dict:
                        if len(module_filename_dict[search_key]) < 2:
                            module_filename_dict[search_key].append(Thermal_csv)
                        else:
                            module_filename_dict[search_key][1] = Thermal_csv
                    else:
                        module_filename_dict[search_key] = [Thermal_csv]
            print(module_filename_dict)

            for module_no, filename in module_filename_dict.items():
                RGB_csv, Thermal_csv = filename  # Unpack the list into separate variables
                object_key_RGB = f"{RGB_image_file_local}/{RGB_csv}"
                object_key_thermal = f"{thermal_image_file_local}/{Thermal_csv}"
                #getting url for reading image from aws bucket
                presigned_url_thermal = object_key_RGB
                presigned_url_RGB=object_key_thermal
                
                if presigned_url_thermal:
                    thermal_url = presigned_url_thermal
                else:
                    logger.error(f"Failed to generate presigned URL for {filename}")
                if presigned_url_RGB:
                    RGB_url=presigned_url_RGB
                else:
                    logger.error(f"Failed to generate presigned URL for {filename}")
                
                module_filename_dict[module_no] = [thermal_url, RGB_url]

    # Update data dictionary with image locations
    for key, value in data.items():
        module_no = value['Module No.']
        filenames_dict = module_filename_dict.get(module_no, [])
        rgb_imagelocation = filenames_dict[0]
        thermal_imagelocation = filenames_dict[1]
        data[key]['rgb_image']=rgb_imagelocation
        data[key]['thermal_image']=thermal_imagelocation

    
    logger.info(data)

    #replacing Temp and character after that with temperature
    for item in data.values():
        for key in list(item.keys()):
            if 'Temp' in key:
                index = key.find('Temp')
                new_key = key[:index] + 'Temperature'
                item[new_key] = item.pop(key)

    logger.info(data)
  
    #meta data for each project:
    data2 = {
        'Customer': '123/23',
        'Site': '(2,12)',
        'capacity': '12MW',
        'location': 'Agra, New Delhi',
        'date': todayStr,
        'inspection_date':'12/02/2023',
    }

    #sorted the main defect data by block no:
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['Block No.']))
    

    #reading template html file
    file_path = os.path.join(TEMPLAT_SRC, TEMPLATE)
    with open(file_path, "r") as file:
     html_template_str = file.read()
    
   # Create a Jinja2 Template object
    html_template = Template(html_template_str)
    reportText = html_template.render(data=sorted_data,**data2)
    
   
    #Save genereate text as a HTML file
    reportPath = os.path.join(DEST_HTML,OUTPUT_HTML)
    with open(reportPath, mode='w') as f:
        f.write(reportText)
    
     # Convert HTML to PDF with specified options
    pdf_file_path = os.path.join(DEST_DIR, OUTPUT_FILENAME)
    if os.path.exists(reportPath):
        HTML(reportPath).write_pdf(pdf_file_path)
        logger.info("PDF conversion successful!")
    else:
        logger.error(f"Error: HTML file '{reportPath}' does not exist.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CAD Table Splitter")
    parser.add_argument("--config", type=str, required=False, help="Path to a YAML configuration file",
                        default="./config_paths/config.yaml")
    args = parser.parse_args()
    logger.info(f"Config file path: {args.config}")
    configuration = AppConfig(args.config)
    logger.info("yaml configuration done fully")
    aws_config = configuration.get_section("aws_path_configuration")  # Get aws_path_configuration section
    csv_file_name = aws_config.get("csv_file_name", "")  # Get csv_file_name value
    thermal_image_file = aws_config.get("thermal_image_file", "")  # Get thermal_image_file value
    RGB_image_file= aws_config.get("RGB_image_file","") # Get RGB_image_File value
    bucket_name= aws_config.get("Bucket_name","") #Get Bucket Name
    local_config=configuration.get_section("local_path_configuration")
    csv_file_name_1_local=local_config.get("csv_file_name_1_local", "") 
    csv_file_name_2_local=local_config.get("csv_file_name_2_local", "") 
    thermal_image_file_local=local_config.get("thermal_image_file","")
    RGB_image_file_local=local_config.get("RGB_image_file_local","")
    logger.info('start generate report...')
    start()
