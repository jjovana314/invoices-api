import React from 'react';
import {
    Row, Col, Button, Card, CardBody, CardHeader, CardFooter, Input,
    InputGroup, InputGroupAddon
} from 'reactstrap';
import './App.css';

class RegisterApp extends React.Component {
    constructor(properties) {
        super(properties);
        this.state = {
            "DebtorCompanyNumber": "",
            "InvoiceNumber": "",
            "Amount": 0.0,
            "IssueDate": "",
            "Comments": "",
            "Lifetime": 0
        }
        this.handleClick = this.handleClick.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        const inputId = event.target.id;
        const inputValue = event.target.value;
        let state = this.state;
        state[inputId] = inputValue;
        this.setState(state);
    }

    handleClick(event) {
        const url = "http://localhost:5000/invoice/register"
        const buttonId = event.target.id;
        let state = this.state;
        if (buttonId === "create") {
            fetch(url, {
                method: 'POST',
                body: JSON.stringify({
                    "DebtorCompanyNumber": state["DebtorCompanyNumber"],
                    "InvoiceNumber": state["InvoiceNumber"],
                    "Amount": state["Amount"],
                    "IssueDate": state["IssueDate"],
                    "Comments": state["Comments"],
                    "Lifetime": state["Lifetime"]
                })
            })
            .then(response =>{
                state["httpStatus"] = response.status;
                state["errorMsg"] = response.statusText;
                if (response.status < 300) {
                    return response.json()
                }
                return {}
            })
        }
    }
}


export default App;
