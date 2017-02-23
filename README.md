## Overview

Exposes the gensim Word2Vec model via a RESTful interface.  Also caches responses.  This only exposes the most_similar method,
and supports the positive, negative, and ntop requests.

## Usage

Note that startup can take several minutes, as the Word2Vec model needs to be loaded into memory.
The server exposes a /keepalive method intended for ELB or other monitoring, and
the keepalive will trigger warmup of the Word2Vec model.  Peak memory usage is around 7GB.


```
$ docker run -d -p 8080:80 reutersmedia/pyword2vec:latest

$ curl http://localhost:8080/most_similar?positive=hello&topn=5
{
  "most_similar": [
    [
      "hi", 
      0.6548985838890076
    ], 
    [
      "goodbye", 
      0.6399056911468506
    ], 
    [
      "howdy", 
      0.6310961246490479
    ], 
    [
      "goodnight", 
      0.5920579433441162
    ], 
    [
      "greeting", 
      0.5855876803398132
    ]
  ], 
  "negative_unused": [], 
  "positive_unused": []
}
```

To query for multiple terms:

```
$ curl "http://localhost:8080/most_similar?positive=hello&positive=world&topn=5"
{
  "most_similar": [
    [
      "g'day", 
      0.5079617500305176
    ], 
    [
      "globe", 
      0.49662062525749207
    ], 
    [
      "OBAMA_Hello", 
      0.4954448640346527
    ], 
    [
      "hi", 
      0.4945191442966461
    ], 
    [
      "guten_tag", 
      0.4936927855014801
    ]
  ], 
  "negative_unused": [], 
  "positive_unused": []
}
```

If a term is not present in the Word2Vec model, it will be excluded from the response and the exclusion will be noted in either the "positive_unused" or "negative_unused" list.

```
$ curl "http://localhost:8080/most_similar?positive=hello&positive=world&positive=flibertygibbet&topn=5"
{
  "most_similar": [
    [
      "g'day", 
      0.5079617500305176
    ], 
    [
      "globe", 
      0.49662062525749207
    ], 
    [
      "OBAMA_Hello", 
      0.4954448640346527
    ], 
    [
      "hi", 
      0.4945191442966461
    ], 
    [
      "guten_tag", 
      0.4936927855014801
    ]
  ], 
  "negative_unused": [], 
  "positive_unused": [
    "flibertygibbet"
  ]
}
```


## Building

In order to build a Docker image, you should download the Google pretrained model to GoogleNews-vectors-negative300.bin.gz and
place it in the root directory.


## Copyright

Copyright (C) 2017 Thomson Reuters