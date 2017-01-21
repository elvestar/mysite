import React, { Component } from 'react'

import { Router, Route, Link, IndexRoute, browserHistory, hashHistory } from 'react-router'

import { ClockItems } from '../components/common/ClockItems.jsx'
import { AllComponents } from '../components/AllComponents.jsx'
import { AdminContentHeader } from '../components/common/Partials.jsx'

class AdminAside extends React.Component {
  render() {
    return (
          <div className="admin-aside">
            <div className="aside-header">
              <a href="/tms" className="m-x aside-title">
                时间管理
              </a>
              <div className="m-x aside-title-extra">
                <a href="">
                  <i className="fa fa-lg fa-clock-o" ></i>
                </a>
              </div>
            </div>
            <div className="aside-body m-t">

              <div className="aside-section project-section">
                <div className="section-header">
                  <a href="#reportSection">
                    <i className="fa fa-caret-right"></i>
                    报表
                  </a>
                </div>
                <div className="section-body">
                  <ul className="section-list">
                    <li className="section-item">
                      <Link to="/tms/report" activeClassName="active">
                        <i className="fa fa-file-text-o"></i>
                        报表
                      </Link>
                    </li>
                    <li className="section-item">
                      <Link to="/tms/project" activeClassName="active">
                        <i className="fa fa-file-text-o"></i>
                        项目
                      </Link>
                    </li>
                    <li className="section-item">
                      <Link to="/tms/all" activeClassName="active">
                        <i className="fa fa-list"></i>
                        全部组件    
                      </Link>
                    </li>
                    <ul>
                </ul>
                  </ul>
                </div>
              </div>
            </div>
          </div>
    )
  }
}

class App extends React.Component {
  render() {
    return (
      <div>
        <div className="admin-main">
        <AdminAside/>

          <div className="admin-content-wrapper">
            <div className="admin-content">
                  {this.props.children}
            </div>
          </div>
        </div>

      </div>
    )
  }
}

class Project extends React.Component {
  render() {
    return (
      <div>
        <AdminContentHeader />
        <div className="admin-content-body m-x m-t">
        <ClockItems/>
        </div>
      </div>
    )
  }
}

class Report extends React.Component {
  render() {
    return (
      <div>
        <AdminContentHeader />
        <div className="admin-content-body m-x m-t">
          <ClockItems />
          <div className="m-r m-t">
            <table className="admin-table">
              <caption>日报列表</caption>
              <thead>
                <tr>
                  <th width="15%">日期</th>
                  <th width="20%">分时图</th>
                  <th className="time-cost">工作</th>
                  <th className="time-cost">学习</th>
                  <th className="time-cost">有效</th>
                  <th className="time-cost">全部</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    )
  }
}

// var history = process.env.NODE_ENV !== 'production' ? browserHistory : hashHistory
var history = hashHistory
export class TMSV2 extends React.Component {
  render() {
    return (
      <Router history={history}>
        <Route path="/tms" component={App}>
          <Route path="all" component={AllComponents} />
          <Route path="project" component={Project} />
          <Route path="report" component={Report} />
        </Route>
      </Router>
    )
  }
}