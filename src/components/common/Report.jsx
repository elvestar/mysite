import React from 'react'

export class Report extends React.Component {
    constructor(props) {
        super(props)
        // this.state = {
        //     report: this.props.report
        // }
    }

    render() {
        return (
            <div>
                <ul>
                    {
                        this.props.report.categories.map((category, index) => {
                            return (
                                <li key={index}>
                                    {category.name}
                                    <span className="pull-right">
                                        {category.pct}
                                        【{category.cost}】
                                                    </span>
                                                    <ul>
                                                        {
                                                            category.projects.map((project, index2) => {
                                                                return (
                                                                    <li key={index2}>
                                                                        * {project.name}
                                                                        <span className="pull-right">
                                                                            {project.pct}
                                                                            【{project.cost}】
                                                                        </span>
                                                                        <ul>
                                                                            {
                                                                                project.things.map((thing, index3) => {
                                                                                    return (
                                                                                        <li key={index3}>
                                                                                            ** {thing.name}
                                                                                            <span className="pull-right">
                                                                                                【{thing.cost}】
                                                                                            </span>
                                                                                        </li>
                                                                                    )
                                                                                })
                                                                            }
                                                                        </ul>
                                                                    </li>
                                                                )
                                                            })
                                                        }
                                                    </ul>
                                                </li>
                                            )
                                        })
                                    }
                                </ul>
                            </div>
           
       ) 
    }
}