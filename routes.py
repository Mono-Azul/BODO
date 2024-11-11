from flask import Flask, render_template, request
import threading
from datetime import datetime
import botec_classes
from botec_classes import get_batch_elements, get_batch_all_elements, get_areas, get_products

fapp = Flask(__name__)

sql_lock = threading.Lock()

index_lock = threading.Lock()
@fapp.route("/index.html")
def index():
    with index_lock:
        return """<h1>Hello, Friends of Botox!</h1>
        <p><a href="./batch-search">Go to search</a>
        </p><img src="./static/unicorn.jpg">"""


@fapp.route("/batch-search")
def hello_test():
    with sql_lock:
        area_list = get_areas()
        product_list = get_products()
        html_str = render_template("batch_search.html", areas=area_list, products=product_list)
        # print(html_str)
        return html_str

@fapp.route("/batches")
def batch_list():
    with sql_lock:
        ifnull = lambda x: None if not x else x

        start_dt = datetime.strptime(request.args.get('start'), "%Y-%m-%dT%H:%M")
        end_dt = datetime.strptime(request.args.get('end'), "%Y-%m-%dT%H:%M")
        area_id = ifnull(request.args.get('areaid'))
        product_id = ifnull(request.args.get('product'))

        batches = botec_classes.get_batches(area_id=area_id, start=start_dt, end=end_dt, product=product_id).values()
        html_str = render_template("batch_list.html", batches=batches)
        #print(html_str)
        return html_str

@fapp.route("/batch/detail/<prid>")
def batch_details(prid=0):
    with sql_lock:
        if prid == 0:
            return """<h1><a href="/index.html">Nothing found</a></h1>"""

        batch = botec_classes.get_batch(prid)
        get_batch_all_elements(batch)
        parameters = botec_classes.get_parameters(prid)

        html_str = render_template("batch_details.html", batch=batch, parameters=parameters)
        #print(html_str)
        return html_str