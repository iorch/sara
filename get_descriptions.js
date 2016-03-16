"use strict";
var conn = new Mongo();
var db = conn.getDB("cms_tramites");

var mr = db.runCommand({
  "mapReduce" : "formalities",
  "map" : function() {
    var key = this._id.str
    var value = { "_index" : "formalities",
    "_type" : "tramite",
    "mongo_id": this._id.str,
    "process_citizen_name": this.process_citizen_name,
    "description_citizen": this.description_citizen,
    "process_online_link": this.process_online_link }
      emit(key,value);
  },
  "reduce" : function(key, stuff) {
    return stuff;
  },
  "out": "links"
});

var cursor = db.getCollection(mr.result).find({"value.process_citizen_name": {$ne:null}},{"_id":1});
var id;
while ( cursor.hasNext() ) {
   id = cursor.next()["_id"];
   printjsononeline( db.getCollection(mr.result).findOne({"_id":id},{"value":1})["value"]);
}
