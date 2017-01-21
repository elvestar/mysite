import React from 'react'
import { Row, Col, Card } from 'antd'

import { AdminContentHeader } from '../components/common/Partials.jsx'
import { ClockItems } from '../components/common/ClockItems.jsx'
import { DayReport } from '../components/common/DayReport.jsx'

export class AllComponents extends React.Component {
    render() {
        return (
            <div>
                <AdminContentHeader/>
                <Row className="m-t">
                    <Col span={24} className="p-x">
                        <Card title="日报" extra={<a href="#">More</a>}>
                            <DayReport date={'2017-01-19'} />
                        </Card>
                    </Col>
                </Row>
                <Row className="m-t">
                    <Col span={6} className="p-x">
                        <Card title="Card title" bordered={true}>
                            <p>Card content</p>
                            <p>Card content</p>
                            <p>Card content</p>
                        </Card>
                    </Col>
                </Row>
            </div>
        )
    }
}