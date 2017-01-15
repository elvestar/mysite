import React from 'react'

export class ClockItems extends React.Component {
    render() {
        return (
            <div className="row dayClockItems">
                <div className="col-md-3 itemStats">
                    <div>
                        <span className="date">
                            2017-01-15
                        </span>
                        <span className="week"> 2015年第5周 </span>
                    </div>
                    <div className="info">共 22 计时项</div>
                    <div className="info">总计 55 小时</div>
                </div>
                <div className="col-md-9 itemList">
                    <ul>
                        <li className="timeGapLg">
                            呵呵
                                </li>
                    </ul>
                </div>
            </div>
        )
    }
}