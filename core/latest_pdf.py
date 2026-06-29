# import os
# import glob
# from decouple import config
# from projectapp.models import ProjectModel

# BASE_SERVER_ADDRESS = config('BASE_SERVER_ADDRESS')

# # BASE_SERVER_ADDRESS = '/var/www/pdfs/'
# # BASE_SERVER_ADDRESS = './pdfs'
# # BASE_SERVER_ADDRESS = './pdfs'

# def generate_latest_pdf_address(company_name: str, location_name: str) -> str | None:
#     ''' generate latest pdf address '''
#     # go to the relevent company folder
#     base_path = os.path.join(BASE_SERVER_ADDRESS, company_name)
#     if not os.path.exists(base_path):
#         return None


#     # find latest gfs in each company folder
#     sorted_gfs = sorted(os.listdir(base_path), reverse=True)
#     if not sorted_gfs:
#         return None

#     latest_gfs = sorted_gfs[0]
#     # total_location_name = location_name.startswith(f'{location_name}')

#     latets_pdf = glob.glob(os.path.join(base_path, latest_gfs, f"{location_name}_*.pdf"))[0]

#     return latets_pdf
