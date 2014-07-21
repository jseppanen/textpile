/** @jsx React.DOM */

var api = "";

var Doc = React.createClass({
  getInitialState: function() {
    return {good:false, bad:false};
  },
  render: function() {
    var relevance_button = <div />;
    if (this.props.doc.relevance !== undefined) {
      var keywords_li = this.props.doc.explain.map(function(e) {
        return <li>{e.score} {e.keyword}</li>;
      });
      relevance_button = (
        <div className="btn-group">
          <button type="button" className="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown">
            {"" + Math.round(100*this.props.doc.relevance) + "% "}
            <span className="caret"></span>
          </button>
          <ul className="dropdown-menu">{keywords_li}</ul>
        </div>
      );
    }
    return (
      <div className={"featurette " + (this.state.bad ? "hidden" : "")}>
        <div className="row">
          <div className="col-md-10">
            <h2 className="featurette-heading">
              <a href={this.props.doc.url}>{this.props.doc.title}</a>&nbsp;
                <span className="pull-right"><small>{this.props.doc.published_date}</small></span>
              {relevance_button}
            </h2>
          </div>
          <div className="col-md-2">
            <h2>
              <button type="button"
                  className={"btn btn-danger pull-right"
                       + (this.state.good ? " disabled" : "")}
                   onClick={this.buttonClick} id="bad">
                <span className="glyphicon glyphicon-remove"></span></button>
              <button type="button"
                   className={"btn btn-" + (this.state.good ? "primary" : "default")
                       + (this.state.good ? " disabled" : "")}
                   onClick={this.buttonClick} id="good">
                <span className={"glyphicon glyphicon-heart" +
                    (this.state.good ? "" : " text-primary")}></span></button>
            </h2>
          </div>
        </div>
        <p className="lead">{this.props.doc.body}</p>
      </div>
    );
  },
  buttonClick: function(evt) {
    var url = api + 'doc/' + this.props.doc.doc_id;
    var label = evt.currentTarget.id;
    // toggle good/bad state
    var st = {};
    var prev_state = this.state[label];
    st[label] = !prev_state;
    this.setState(st);
    $.ajax({
      url: url,
      dataType: 'json',
      type: 'POST',
      data: {label: label},
      success: function(data) {
        //this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, error) {
        // undo state change
        var st = {};
	st[label] = prev_state;
        this.setState(st);
        console.error(url, status, error.toString());
      }.bind(this)
    });
    this.props.scrollListener();
    return false;
  }
});

function topPosition(domElt) {
  if (!domElt) {
    return 0;
  }
  return domElt.offsetTop + topPosition(domElt.offsetParent);
}

var DocList = React.createClass({
  getDefaultProps: function () {
    return {
      pageSize: 10,
      threshold: 250
    };
  },
  getInitialState: function() {
    return {docs: [],
            offset: 0,
            hasMore: true};
  },

  componentWillMount: function() {
    //this.loadMoreDocs();
  },
  componentDidMount: function () {
    this.attachScrollListener();
  },
  componentDidUpdate: function () {
    this.attachScrollListener();
  },
  componentWillUnmount: function () {
    this.detachScrollListener();
  },

  loadMoreDocs: function() {
    var url = api + this.props.page;
    $.ajax({
      url: url,
      data: {num:this.props.pageSize, offset:this.state.offset},
      dataType: 'json',
      success: function(data) {
        console.log('got docs: ' + this.props.page + ": " + data.results.length);
        this.setState({docs: this.state.docs.concat(data.results),
                       offset: this.state.offset + data.results.length,
                       hasMore: data.results.length == this.props.pageSize});
      }.bind(this),
      error: function(xhr, status, error) {
        console.error(url, status, error.toString());
      }.bind(this)
    });
  },

  render: function() {
    if (!this.props.active)
      return <div className="hidden" />
    console.log("DocList render: " + this.props.page);
    var sl = this.scrollListener.bind(this);
    var docs = this.state.docs.map(function (doc) {
      return <Doc doc={doc} key={doc.doc_id} scrollListener={sl} />;
    });
    return (
      <div className="container marketing">
          {docs}
          {this.state.hasMore ? <p className="bg-info">Loading...</p> : ''}
        <hr className="featurette-divider" />
      </div>
    );
  },

  scrollListener: function () {
    if (!this.props.active)
      return;
    var el = this.getDOMNode();
    var scrollTop = (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop;
    if (topPosition(el) + el.offsetHeight - scrollTop - window.innerHeight < Number(this.props.threshold)) {
      this.loadMoreDocs();
      this.detachScrollListener();
    }
  },
  attachScrollListener: function () {
    if (!this.state.hasMore) {
      return;
    }
    window.addEventListener('scroll', this.scrollListener);
    this.scrollListener();
  },
  detachScrollListener: function () {
    window.removeEventListener('scroll', this.scrollListener);
  }

});

var Navbar = React.createClass({
  getInitialState: function() {
    return {num_docs:0, num_good:0, num_bad:0, last_updated:""};
  },
  componentWillMount: function() {
    $.ajax({
      url: api + 'stats',
      dataType: 'json',
      success: function(data) {
        this.setState(data.results);
      }.bind(this),
      error: function(xhr, status, error) {
        console.error(url, status, error.toString());
      }.bind(this)
    });
  },
  render: function() {
    return (
      <nav className="navbar navbar-default navbar-static-top" role="navigation">
        <div className="container">
          <ul className="nav navbar-nav">
            <li className={this.props.page == "most_relevant" ? "active" : ""}>
              <a href="#" onClick={this.click} id="most_relevant">
                {this.state.num_docs} ilmoa</a></li>
            <li className={this.props.page == "tagged/good" ? "active" : ""}>
              <a href="#" onClick={this.click} id="tagged/good">
                {this.state.num_good} hyvää</a></li>
            <li className={this.props.page == "tagged/bad" ? "active" : ""}>
              <a href="#" onClick={this.click} id="tagged/bad">
                {this.state.num_bad} huonoa</a></li>
            <li className={this.props.page == "random" ? "active" : ""}>
              <a href="#" onClick={this.click} id="random">
                random</a></li>
          </ul>
          <p className="navbar-text navbar-right">Päivitetty {this.state.last_updated}</p>
        </div>
      </nav>
    );
  },
  click: function(evt) {
    this.props.set_page(evt.currentTarget.id);
    return false;
  }
});

var App = React.createClass({
  getInitialState: function() {
    return {page:'most_relevant'};
  },
  set_page: function(page) {
    this.setState({page: page});
  },
  render: function() {
    return (
    <div>
      <Navbar page={this.state.page} set_page={this.set_page.bind(this)} />
      <DocList page="most_relevant" active={this.state.page == "most_relevant"} />
      <DocList page="tagged/good" active={this.state.page == "tagged/good"} />
      <DocList page="tagged/bad" active={this.state.page == "tagged/bad"} />
      <DocList page="random" active={this.state.page == "random"} />
      <footer className="container">
        <p className="pull-right">Jee!</p>
      </footer>
    </div>
    );
  }
});

React.renderComponent(
  <App />, document.body
);
