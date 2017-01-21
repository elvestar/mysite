import React from 'react'
import $ from 'jquery';
import moment from 'moment'
import echarts from 'echarts'

export class ClockItems extends React.Component {
    constructor(props) {
        super(props)
        moment.locale('zh-cn')
    }
    render() {
        return (
            <div className="row dayClockItems">
                <div className="col-md-3 itemStats">
                    <div>
                        <span className="date">
                            {this.props.date.locale('zh-cn').format('LL')}
                        </span>
                        <span className="week">{this.props.date.format('dddd')}
  </span>
                    </div>
                    <div className="info">共 {this.props.clockItems.length} 计时项</div>
                </div>
                <div className="col-md-9 itemList">
                    <ul>
                        {
                            this.props.clockItems.map((item, index) => {
                                if (true) {
                                    return (
                                        <li className="clockItem" key={index}>
                                            <span className="time">
                                                <span>
                                                    {moment(item.start_time).format('HH:mm')}
                                                </span>
                                                -
                                            <span>
                                                    {moment(item.end_time).format('HH:mm')}
                                                </span>
                                            </span>
                                            <span className="thing">
                                                {item.thing}
                                            </span>
                                            <span className="pull-right">
                                                <span className="cost">{item.time_cost_min}</span>
                                                <span className="projectInfo">
                                                    <span className="project text-success">{item.project} </span>
                                                    <span className="label label-success">{item.category}</span>
                                                </span>
                                            </span>
                                        </li>
                                    )

                                } else {
                                    return (
                                        <li className="timeGapLg" key={index}>{item.thing}</li>
                                    )
                                }
                            })
                        }
                    </ul>
                </div>
            </div>
        )
    }
}