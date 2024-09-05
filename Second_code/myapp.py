from typing import Union
import logging
import logging.config
from fastapi import FastAPI, Request
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG


class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_logging()
        self.setup_routes()
        self.app.middleware("http")(self.log_requests)

    def setup_logging(self):
        log_file = "app.log"
        # setup file handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_format = "%(asctime)s %(levelname)-8s : %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(file_format, datefmt=date_format)
        file_handler.setFormatter(formatter)

        # configure logging for uvicorn
        LOGGING_CONFIG["formatters"]["access"][
            "fmt"
        ] = "%(asctime)s %(levelname)-8s : %(message)s"
        LOGGING_CONFIG["formatters"]["default"][
            "fmt"
        ] = "%(asctime)s %(levelname)-8s : %(message)-8s"
        LOGGING_CONFIG["formatters"]["default"]["datefmt"] = date_format
        LOGGING_CONFIG["formatters"]["access"]["datefmt"] = date_format

        LOGGING_CONFIG["handlers"]["default"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "level": "INFO",
            "filename": log_file,
        }
        LOGGING_CONFIG["handlers"]["access"] = {
            "class": "logging.FileHandler",
            "formatter": "access",
            "level": "INFO",
            "filename": log_file,
        }
        logging.config.dictConfig(LOGGING_CONFIG)
        self.log = logging.getLogger("uvicorn")
    def setup_routes(self):
        @self.app.get('/')
        def read_root():
            return {'message': 'Hello, World!'}
        @self.app.get('/items/{item_id}')
        def read_item(item_id: int, q: Union[str, None] = None):
            return {'item_id': item_id, 'q': q}
        
    async def log_requests(self,request: Request, call_next):
        response: Response = await call_next(request)
        
        # Determine log level based on status code
        if response.status_code==200:
            self.log.info(f"Request {request.method} {request.url} called with {response.status_code} status")
        else:
            self.log.error(f"Request {request.method} {request.url} called with {response.status_code} status")
        
        #########################################################
        # code given by tabnine don't know it's working u can check if it's working
        # if response.status_code >= 500:
        #     log_level = logging.ERROR
        # elif response.status_code >= 400:
        #     log_level = logging.WARNING
        # elif response.status_code >= 300:
        #     log_level = logging.INFO
        # else:
        #     log_level = logging.DEBUG
        
        # # Log request details
        # self.log.log(
        #     log_level,
        #     f"{request.method} {request.url} - {response.status_code}"
        # )
        
        return response
    
app_inst = MyApp()
app=app_inst.app