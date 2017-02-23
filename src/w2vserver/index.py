from flask import Flask, request, jsonify, abort
import sys
import logging
import json
import os
import gensim
import threading

from logstash.formatter import LogstashFormatterVersion1
from logging.handlers import RotatingFileHandler

#### LOGGING SETUP ####

class LogstashFormatter(LogstashFormatterVersion1):
    @classmethod
    def serialize(cls,message):
        return json.dumps(message)

log_level = os.getenv("LOG_LEVEL","INFO")
try:
    numeric_level = getattr(logging, log_level)
except:
    print("Invalid log level: {0}".format(log_level))
    numeric_level = logging.INFO

root = logging.getLogger()

root.setLevel(numeric_level)

handler = RotatingFileHandler(os.getenv("PYTHON_LOG_FILE","/var/log/w2vserver.log"),
                              mode='ab',
                              maxBytes=1000000,
                              backupCount=2)
handler.setFormatter(LogstashFormatter(tags=['python']))
root.addHandler(handler)



#------------------------------------------------------------------------
# App maintenance -- APP IS STARTED AT THE END OF THE FILE
#------------------------------------------------------------------------

_model_lock = threading.Lock()
_w2v = None

def get_model():
    global _model_lock
    global _w2v
    if _w2v is None:
        _model_lock.acquire(True)
        try:
            if _w2v is None:
                _w2v = gensim.models.Word2Vec.load_word2vec_format("/GoogleNews-vectors-negative300.bin.gz",binary=True)
                _w2v.init_sims(replace=True)
        finally:
            _model_lock.release()
    return _w2v



# App instance
application = Flask(__name__)

LOGGER = logging.getLogger(__name__)

def filter_words(w2v,words):
    present, absent = [],[]
    for w in words:
        (absent,present)[w in w2v].append(w)
    return present,absent

@application.route("/most_similar",methods=['GET'])
def most_similar():
    pos = request.args.getlist('positive')
    neg = request.args.getlist('negative')
    topn = request.args.get('topn')

    if topn is not None:
        try:
            topn = int(topn)
        except:
            LOGGER.exception("Bad topn parameter {0}, using default 10".format(topn))
            topn = 10
    else:
        topn = 10

    if pos is None:
        pos = []
    if neg is None:
        neg = []
        
    w2v = get_model()
    pos_good,pos_bad = filter_words(w2v,pos)
    neg_good,neg_bad = filter_words(w2v,neg)

    if len(pos_good)>0 or len(neg_good)>0:
        r = w2v.most_similar(positive=pos_good,negative=neg_good,topn=topn)
    else:
        r = []
        
    return jsonify({'most_similar':r,
                    'positive_unused': pos_bad,
                    'negative_unused': neg_bad})

        
@application.route("/keepalive",methods=['GET'])
def keepalive():
    # keepalive will warm up model
    get_model()
    return "OK"


if __name__ == '__main__':
    application.run(debug=True)

