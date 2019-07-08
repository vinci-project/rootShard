import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers

import time, json, datetime, os

class elalog:
    def __init__(self, date):

        es_host = os.getenv("ES_PORT_9200_TCP_ADDR") or '<%ELASTICIP%>'
        es_port = os.getenv("ES_PORT_9200_TCP_PORT") or '9200'
        self.lastDate = date
        self.es = Elasticsearch([{'host': es_host, 'port': es_port}])

        # BLOCKS INDEX
        self.blocks_index_name = "blocks-" + date
        self.block_mapping = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 0
            },
            "mappings": {
                        "blocks-" + date: {
                            "properties": {
                                "@dtime": {
                                    "type": "date",
                                    "format": "epoch_second"
                                },
                                "hash": {
                                    "type": "text"
                                },
                                "signatures": {
                                    "type": "text"
                                },
                                "tcount": {
                                    "type": "long"
                                },
                                "validator": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "bheight": {
                                    "type": "long"
                                }
                            }
                        }
                    }
        }

        if self.es.indices.exists(self.blocks_index_name):
            try:
                self.es.indices.delete(index=self.blocks_index_name)
                self.es.indices.create(index=self.blocks_index_name, body=self.block_mapping)
            except elasticsearch.ElasticsearchException as es1:
                print("Elastic exception on create Indicies:", es1)
        else:
            self.es.indices.create(index=self.blocks_index_name, body=self.block_mapping)


        # TRANSACTIONS INDEX
        self.transactions_index_name = "transactions-" + date
        self.transactions_mapping = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 0
            },
            "mappings": {
                        "transactions-" + date: {
                            "properties": {
                                "@dtime": {
                                    "type": "date",
                                    "format": "epoch_second"
                                },
                                "sender": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "receiver": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "token_count": {
                                    "type": "float"
                                },
                                "token_type": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "hash": {
                                    "type": "text"
                                },
                                "block": {
                                    "type": "long"
                                }
                            }
                        }
                    }
        }
        if self.es.indices.exists(self.transactions_index_name):
            try:
                self.es.indices.delete(index=self.transactions_index_name)
                self.es.indices.create(index=self.transactions_index_name, body=self.transactions_mapping)
            except elasticsearch.ElasticsearchException as es1:
                print("Elastic exception on create Indicies:", es1)
        else:
            self.es.indices.create(index=self.transactions_index_name, body=self.transactions_mapping)

        # BALANCE HISTORY
        self.balance_index_name = "balance"
        self.balance_mapping = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 0
            },
            "mappings": {
                        "balance": {
                            "properties": {
                                "@dtime": {
                                    "type": "date",
                                    "format": "epoch_second"
                                },
                                "user": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "balance": {
                                    "type": "float"
                                }
                            }
                        }
                    }
                }

        if self.es.indices.exists(self.balance_index_name):
            try:
                 self.es.indices.delete(index=self.balance_index_name)
                 self.es.indices.create(index=self.balance_index_name, body=self.balance_mapping)
            except elasticsearch.ElasticsearchException as es1:
                print("Elastic exception on create Indicies:", es1)
        else:
            self.es.indices.create(index=self.balance_index_name, body=self.balance_mapping)

        # VALIDATOR STATISTIC
        self.clients_index_name = "clients"
        self.clients_mapping = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 0
            },
            "mappings": {
                        "clients": {
                            "properties": {
                                "@dtime": {
                                    "type": "date",
                                    "format": "epoch_second"
                                },
                                "ip": {
                                    "type": "ip"
                                },

                                "geoip": {
                                    "properties": {
                                        "city_name": {
                                            "type": "text"
                                        },
                                        "continent_name": {
                                            "type": "text"
                                        },
                                        "country_iso_code": {
                                            "type": "text"
                                        },
                                        "location": {
                                            "type": "geo_point"
                                        },
                                        "region_name": {
                                            "type": "text"
                                        }
                                    }
                                },
                                "public_key": {
                                    "type": "text",
                                    "fielddata": True
                                },
                                "client_type": {
                                    "type": "text",
                                    "fielddata": True
                                }
                            }
                        }
                    }
        }
        if self.es.indices.exists(self.clients_index_name):
            try:
                self.es.indices.delete(index=self.clients_index_name)
                self.es.indices.create(index=self.clients_index_name, body=self.clients_mapping)
            except elasticsearch.ElasticsearchException as es1:
                print("Elastic exception on create Indicies:", es1)
        else:
            self.es.indices.create(index=self.clients_index_name, body=self.clients_mapping)

    def elasticClients(self, jsons:list):
        try:
            helpers.bulk(self.es, jsons)
        except elasticsearch.ElasticsearchException as es1:
            print("Elastic exception on save Validators:", es1)

        print("Save Validators in elastic!")

    def elasticBlock(self, timestamp:float, validator:str, tcount:int, signatures:list, hash:str, bheight:int):
        index = 'blocks-' + self.lastDate
        estype = 'blocks-' + self.lastDate
        eljson = json.dumps({"@dtime": int(timestamp), "validator": validator, "tcount": tcount, "signatures": list(signatures), "hash": hash, "bheight": bheight}, separators=(',', ':'))
        try:
            self.es.index(index=str(index).lower(), doc_type=estype.lower(), body=eljson)
        except elasticsearch.ElasticsearchException as es1:
            print("Elastic exception on send Block:", es1)

    def elasticTransaction(self, jsons:list):
        try:
            helpers.bulk(self.es, jsons)
        except elasticsearch.ElasticsearchException as es1:
            print("Elastic exception on save bulk Transactions:", es1)


    def elasticBalanceHistory(self, balance:dict):
        users = balance.keys()
        jsonMas = []

        print("USER LEN:", len(users))

        for user in users:
            eljson = {"_index": "balance", "_type": "balance", "_id": user,
                      "_source": {"@dtime": int(time.time()), "user": user,
                                  "balance": balance.get(user)}}
            jsonMas.append(eljson)

        try:
            helpers.bulk(self.es, jsonMas)
        except elasticsearch.ElasticsearchException as es1:
            print("Elastic exception on save balance:", es1)


    def getLastEBlock(self):
        query = {"aggs" : {
                        "max_blnum":{"max":{"field":"bheight"}}
                    },"size": 0
                }
        try:
            answer = self.es.search(index="blocks-" + self.lastDate, doc_type="blocks-" + self.lastDate, body=query)

            if not answer["aggregations"]["max_blnum"]["value"] == None:
                return int(answer["aggregations"]["max_blnum"]["value"])
            else:
                return 0
        except elasticsearch.ElasticsearchException as es1:
            print("Elastic exception on search last block index:", es1)
