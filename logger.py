# To avoid circular imports
def log_output(string: str, tagName: str = "default"):
    print(string)
    
log_output = print

def set_logger(fn):
    global log_output
    log_output = fn