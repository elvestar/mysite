import React, { Component } from 'react'
import { render } from 'react-dom'

import { TMSV2 } from './components/TMSV2'

require("./css/admin.scss");
require("./css/styles.scss");
require("./css/new_styles.scss");


render(
  <TMSV2 />,
  document.getElementById('app')
)