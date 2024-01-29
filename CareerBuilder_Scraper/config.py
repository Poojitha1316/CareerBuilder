# config.py

class Config:
    URL_TEMPLATE = "https://www.careerbuilder.com/jobs?cb_apply=false&cb_workhome=all&emp=jtct%2Cjtc2%2Cjtcc&keywords={keyword}&location=&pay=&posted=&sort=date_desc&page={page}"
    OUTPUT_FILENAME_TEMPLATE = "output.csv"
    KEYWORD = "data analyst"
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    PROXY = "http://dc0950da5da2e980256957106ccdf277fca47202:@proxy.zenrows.com:8001"
