# ROOT-shard API documentation
This is a description of the API for the interaction between nodes implemented over HTTP transport. The document is intended for developers and researchers of block-technologies.   

## REST API Documentation
Description of REST API for requesting data from root nodes over the HTTP protocol.

### Oracle API

**Endpoint name:** /oracle/exchangeRate  
**Description:** Endpoint for requesting exchange rate of currencies  
**Method:** GET  
**Parameters:**
* "SOURCE"
* "PAIR"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusAttrNotFound_SOURCE                      | 614 | CAN NOT FIND ATTRIBUTE - SOURCE
| StatusAttrNotFound_PAIR                        | 615 | CAN NOT FIND ATTRIBUTE - PAIR
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/exchangeRate?SOURCE=NASDAQ&PAIR=USD/EUR
```
**Answer example:**
```json
{"RATE":{"COUNT":"1","DT":"2018-09-28 17-49-21","VALUE":"91.9613"}}
```

___

**Endpoint name:** /oracle/exchangePairs  
**Description:** Endpoint for requesting exchange types for using in exchangeRate  
**Method:** GET  
**Parameters:**
* NONE

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/exchangePairs
```
**Answer example:**
```json
{"PAIRS":["USD/EUR"]}
```

___

**Endpoint name:** /oracle/exchangeRateSourceList  
**Description:** Endpoint for requesting exchange rate sources  
**Method:** GET  
**Parameters:** NONE

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/exchangeRateSourceList
```
**Answer example:**
```json
{"SOURCES":[{"SOURCE_NAME":"TEST-STOCK","URL":"https://test-stock.com/daily_json.js"}]}
```
___

**Endpoint name:** /oracle/stockPrice  
**Description:** Endpoint for requesting current stock price  
**Method:** GET  
**Parameters:**
* "SOURCE"
* "TICKER"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusAttrNotFound_SOURCE                      | 614 | CAN NOT FIND ATTRIBUTE - SOURCE
| StatusAttrNotFound_TICKER                      | 616 | CAN NOT FIND ATTRIBUTE - TICKER
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/stockPrice?SOURCE=ALPHAVANTAGE&TICKER=AA
```
**Answer example:**
```json
{"PRICE":{"COUNT":"1","DT":"2018-09-28 17-49-27","VALUE":"70.8200"}}
```
___

**Endpoint name:** /oracle/stockTickers  
**Description:** Endpoint for requesting stock tickers for using in stockPrice  
**Method:** GET  
**Parameters:**
* NONE

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/stockTickers
```
**Answer example:**
```json
{"TICKERS":["AA","AAC","AAN","AAP","ABB","ABBV","ABC","ABEV","ABR","ABR-A","ABR-B","ABR-C","ABT","ACCO","ACH","ACM","ACN","ADC","ADM","ADNT","ADS","ADX","AEB","AED","AEE","AEM","AEO","AEP","AER","AFC","AFG","AFGE","AFGH","AFST","AFT","AG","AGCO","AGM-A","AGM-B","AGM.A","AGO-B","AGO-E","AGO-F","AGR","AHC","AHH","AHL","AHL-C","AHT-D","AHT-F","AHT-G","AHT-H","AIC","AIF","AIG","AIT","AIV","AIV-A","AIW","AIY","AJRD","AJX","AJXA","AKO.A","AKS","AL","ALB","ALE"]}
```

___

**Endpoint name:** /oracle/stockPriceSourceList  
**Description:** Endpoint for requesting stock price sources  
**Method:** GET  
**Parameters:**
* NONE

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:5000/oracle/stockPriceSourceList
```
**Answer example:**
```json
{"SOURCES":[{"SOURCE_NAME":"ALPHAVANTAGE","URL":"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"}]}
```
___

**Endpoint name:** /oracle/shardsList  
**Description:** Endpoint for requesting a list of all shards in Vncsphere ecosystem  
**Method:** GET  
**Parameters:**
* NONE

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http
http://x.x.x.x:port/oracle/shardsList
```
**Answer example:**
```json

```
___

**Endpoint name:** /oracle/shardInfo  
**Description:** Endpoint for requesting information about shard  
**Method:** GET  
**Parameters:**
* "NAME"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http

```
**Answer example:**
```json

```
___

**Endpoint name:** /oracle/regShard  
**Description:** Endpoint for registering a new shard in Vncsphere ecosystem  
**Method:** POST  
**Parameters:**
* "NAME"
* "DESCR"
* "TRAN"
* "SIGN"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK

**Request example:**
```http

```
**Answer example:**
```json

```
___

**Endpoint name:** /oracle/updateShard  
**Description:** Endpoint for updating a registered shard  
**Method:** POST  
**Parameters:**
* "NAME"
* "DESCR"
* "TRAN"
* "SIGN"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK

**Request example:**
```http

```
**Answer example:**
```json

```
___

**Endpoint name:** /oracle/checkSum  
**Description:** Endpoint for requesting a hash of any block in any Vncsphere shard  
**Method:** GET  
**Parameters:**
* "NAME"
* "BNUM"

**Possible answers:**

| Answer | Answer code | Description |
| --- | :---: | --- |
| StatusOk 						    | 200 | OK
| StatusDataNotFound           | 628 | DATA NOT FOUND

**Request example:**
```http

```
**Answer example:**
```json

```

___
