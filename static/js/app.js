function FeaturedRequest(id, title, description, client, priority, target_date, product_area) {
  var self = this;
  self.id = id;
  self.title = title;
  self.description = description;
  self.client = ko.observable(client);
  self.priority = priority;
  self.target_date = target_date ? target_date.substr(0,10) : null;
  self.product_area = ko.observable(product_area);

  self.action = ko.computed(function() {
    return self.id == 0 ? 'New' : 'Edit';
  });
}

function FeatureRequestViewModel() {
  var self = this;

  self.requests = ko.observableArray([]); 
  self.freq = ko.observable();
  self.clients = [
    { client_id: 1, name: "Client A"},
    { client_id: 2, name: "Client B"},
    { client_id: 3, name: "Client C"}
  ];    

  self.product_areas = [
    { product_area_id: 1, area: "Policies" },
    { product_area_id: 2, area: "Billing" },
    { product_area_id: 3, area: "Claim" },
    { product_area_id: 4, area: "Reports" },
  ];

  self.freq(null);

  self.startNewRequest = function(){
    self.freq( new FeaturedRequest(0, "","", self.clients[0], 1, null, self.product_areas[0]) );
  };

  self.goToFeatureRequest = function(data){
    self.freq( new FeaturedRequest(data.id, data.title, data.description, data.client(), data.priority, data.target_date, data.product_area()) );
  }

  self.refreshRequestsList = function(allData){
    var mappedReqs = $.map(allData, function(item) { 
      var client = $.grep(self.clients, function(e){ return e.client_id == item.client_id; });
      var product_area = $.grep(self.product_areas, function(e){ return e.product_area_id == item.product_area_id; });
      return new FeaturedRequest(item.id, item.title, item.description, client.length ? client[0] : null, 
                                 item.priority, item.target_date, product_area.length ? product_area[0] : null); 
    });
    self.requests(mappedReqs);

  };

  self.deleteRequest = function(){
    var id = self.freq().id;
    console.log('deleteRequest for '+id);

    if (id > 0){
      $.ajax("/api/v1.0/feature_requests/"+id, {
        type: "DELETE", contentType:"application/json",
        success: function(result) {
          alert(result.msg);
          self.freq(null);
          $.getJSON("/api/v1.0/feature_requests", self.refreshRequestsList);
        }  
      });
    }
  };

  self.addFreq = function(){
    var data = {
      title: self.freq().title,
      description: self.freq().description,
      client_id: self.freq().client().client_id,
      priority: self.freq().priority,
      target_date: self.freq().target_date + ' 00:00:00',
      product_area_id: self.freq().product_area().product_area_id
    };

    var id = self.freq().id;
    if (id > 0){
      $.ajax("/api/v1.0/feature_requests/"+id, {
        data: ko.toJSON(data),
        type: "PUT", contentType:"application/json",
        success: function(result) {
          self.freq(null);
          $.getJSON("/api/v1.0/feature_requests", self.refreshRequestsList);
        }  
      });

    } else {  
      $.ajax("/api/v1.0/feature_requests", {
        data: ko.toJSON(data),
        type: "post", contentType:"application/json",
        success: function(result) {
          if (result.constructor === String ) result = JSON.parse(result);
          self.refreshRequestsList(result);
          self.freq(null);
        }  
      });
    }
  };


  $.getJSON("/api/v1.0/feature_requests", self.refreshRequestsList);

}

ko.applyBindings(new FeatureRequestViewModel());
