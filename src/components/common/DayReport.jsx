import React from 'react'
import $ from 'jquery'
import moment from 'moment'

import { DatePicker, Tabs, Tag, Button, Icon } from 'antd'
import notification from 'antd'
const TabPane = Tabs.TabPane

import { ClockItems } from './ClockItems.jsx'
import { Report } from './Report.jsx'



export class DayReport extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            today: moment(),
            clockItems: [],
            report: { categories: [] },
            stats: {},
            rawData: ''
        }
        if (this.props.date != null) {
            this.state.date = moment(this.props.date)
        } else {
            this.state.date = moment()
        }

        this.pickDate = (date, dateString) => {
            pickDate(moment(date))
        }

        this.pickDate = (date) => {
            if (date == null) {
                notification['warning']({
                    message: '日期不能为空'
                })
                return
            }
            if (date > this.state.today) {
                notification['warning']({
                    message: '所选日期是未来的日期',
                    description: '但是还是给你显示！'
                })
            }
            console.log(date.format('LL'))
            this.setState({
                date: date
            })
            this.getData(date.format('YYYY-MM-DD'))
        }

        this.pickNextDate = () => {
            var nextDate = moment(this.state.date).add(1, 'days')
            this.pickDate(nextDate)
        }
        this.pickPrevDate = () => {
            var prevDate = moment(this.state.date).subtract(1, 'days')
            this.pickDate(prevDate)
        }
        this.pickNextWeek = () => {
            var nextWeek = moment(this.state.date).add(1, 'weeks')
            this.pickDate(nextWeek)
        }
        this.pickPrevWeek = () => {
            var prevWeek = moment(this.state.date).subtract(1, 'weeks')
            this.pickDate(prevWeek)
        }
        this.pickToday = () => {
            this.pickDate(this.state.today)
        }
        this.pickYesterday = () => {
            var yesterday = moment(this.state.today).subtract(1, 'days')
            this.pickDate(yesterday)
        }
        this.pickThisSunday = () => {
            var thisSunday = moment(this.state.today).startOf('week')
            this.pickDate(thisSunday)
        }
        this.pickSameDayPrevMonth = () => {
            var sameDayPrevMonth = moment(this.state.today).subtract(1, 'months')
            this.pickDate(sameDayPrevMonth)
        }
        this.pickSameDayPrevYear = () => {
            var sameDayPrevYear = moment(this.state.today).subtract(1, 'years')
            this.pickDate(sameDayPrevYear)
        }

        this.getData = (dateString) => {
            $.get(`/tms/api/v1/day_stats/?date=${dateString}`, function (data) {
                this.setState({
                    clockItems: data.clock_items,
                    report: data.report,
                    stats: data.days_stats,
                    rawData: JSON.stringify(data)
                })
            }.bind(this))
        }
    }

    componentDidMount() {
        this.pickDate(this.state.date)
    }

    clickTab(key) {
        console.log(key)
    }

    render() {
        return (
            <div>
                <div>
                    <DatePicker onChange={this.pickDate} value={this.state.date} allowClear="false" size="large" />
                    <span className="m-l-xs">
                        <Button.Group>
                            <Button type="ghost" onClick={this.pickPrevWeek}>
                                <Icon type="double-left" />
                            </Button>
                            <Button type="ghost" onClick={this.pickPrevDate}>
                                <Icon type="left" />
                            </Button>
                            <Button onClick={this.pickToday}>今天呵呵</Button>
                            <Button type="ghost" onClick={this.pickNextDate}>
                                <Icon type="right" />
                            </Button>
                            <Button type="ghost" onClick={this.pickNextWeek}>
                                <Icon type="double-right" />
                            </Button>
                        </Button.Group>
                    </span>
                    <span className="m-l-xs">
                        <Button.Group>
                            <Button type="ghost" onClick={this.pickYesterday}>昨天</Button>
                            <Button type="ghost" onClick={this.pickThisSunday}>上周日</Button>
                            <Button type="ghost" onClick={this.pickSameDayPrevMonth}>上月今天</Button>
                            <Button type="ghost" onClick={this.pickSameDayPrevYear}>去年今天</Button>
                        </Button.Group>
                    </span>
                </div>
                <div className="m-t">
                    <Tabs defaultActiveKey="1" onChange={this.clickTab}>
                        <TabPane tab="日报" key="1">
                            <Report report={this.state.report} />
                        </TabPane>
                        <TabPane tab="计时项" key="2">
                            <ClockItems date={this.state.date} clockItems={this.state.clockItems} />
                        </TabPane>
                        <TabPane tab="情景分析" key="3">Content of Tab Pane 3</TabPane>
                        <TabPane tab="原始数据" key="4">
                            <h3>stats</h3>
                            <pre>
                                {JSON.stringify(this.state.stats)}
                            </pre>
                            <h3>report</h3>
                            <pre>
                                {JSON.stringify(this.state.report)}
                            </pre>
                            <h3>clockItems</h3>
                            <pre>
                                {JSON.stringify(this.state.clockItems)}
                            </pre>
                            <h3>rawData</h3>
                            <pre>
                                {JSON.stringify(this.state.rawData)}
                            </pre>
                        </TabPane>
                    </Tabs>
                </div>
            </div>
        )
    }
}