json_schema_1 = {
                                    "title": "Invoice",
                                    "description": "Extract information from an invoice",
                                    "type": "object",
                                    "properties": {
                                        "Vendor No.": {
                                            "title": "Vendor No.",
                                            "description": "Identify the ID of the vendor",
                                            "type": "string"
                                        },
                                        "Vendor Name": {
                                            "title": "Vendor Name",
                                            "description": "Identify the name of the vendor",
                                            "type": "string"
                                        },
                                        "Account No.": {
                                            "title": "Account No.",
                                            "description": "Identify the account number",
                                            "type": "string"
                                        },
                                        "Property Address": {
                                            "title": "Property Address",
                                            "description": "Identify the Property Address",
                                            "type": "string"
                                        },
                                        "Posted Purchase Invoice": {
                                            "title": "Posted Purchase Invoice",
                                            "description": "Identify the Posted Purchase Invoice",
                                            "type": "string"
                                        },
                                        "Invoice Date": {
                                            "title": "Invoice Date",
                                            "description": "Identify the Invoice Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge Start Date": {
                                            "title": "Fixed Charge Start Date",
                                            "description": "Identify the Fixed Charge Start Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge End Date": {
                                            "title": "Fixed Charge End Date",
                                            "description": "Identify the Fixed Charge End Date",
                                            "type": "string"
                                        },
                                        "Fixed Charge for Water Service": {
                                            "title": "Fixed Charge for Water Service",
                                            "description": "Identify the Fixed Charge for Water Service",
                                            "type": "string"
                                        },
                                        "Fixed Charge for Waste Water": {
                                            "title": "Fixed Charge for Waste Water",
                                            "description": "Identify the Fixed Charge for Waste Water",
                                            "type": "string"
                                        },
                                        "Total Fixed Charges": {
                                            "title": "Total Fixed Charges",
                                            "description": "Identify the Total Fixed Charges",
                                            "type": "string"
                                        }
                                    },
                                    "required": ["Vendor No.", "Vendor Name", "Account No.", "Property Address", "Posted Purchase Invoice", "Invoice Date", "Fixed Charge Start Date", "Fixed Charge End Date", "Fixed Charge for Water Service", "Fixed Charge for Waste Water", "Total Fixed Charges"]
                                }
json_schema_2 = {
                                    "title": "Invoice",
                                    "description": "Extract information from an invoice",
                                    "type": "object",
                                    "properties": {
                                        "line_items": {
                                            "title": "Line Items",
                                            "description": "Details of line items such as Water Oncharging",
                                            "type": "array",
                                            "items": {
                                                "title": "Line Item",
                                                "description": "Extract information from each line item of Water Oncharging",
                                                "type": "object",
                                                "properties": {
                                                    "Reading From (Date)": {
                                                        "title": "Reading From (Date)",
                                                        "description": "Identify the Reading From (Date)",
                                                        "type": "string"
                                                    },
                                                    "Reading To (Date)": {
                                                        "title": "Reading To (Date)",
                                                        "description": "Identify the Reading To (Date)",
                                                        "type": "string"
                                                    },
                                                    "No. of Days": {
                                                        "title": "No. of Days",
                                                        "description": "Identify the number of Days",
                                                        "type": "string"
                                                    },
                                                    "Meter No.": {
                                                        "title": "Meter No.",
                                                        "description": "Identify the Meter No.",
                                                        "type": "string"
                                                    },
                                                    "Last Reading": {
                                                        "title": "Last Reading",
                                                        "description": "Identify the Last Reading",
                                                        "type": "string"
                                                    },
                                                    "This Reading": {
                                                        "title": "This Reading",
                                                        "description": "Identify the This Reading",
                                                        "type": "string"
                                                    },
                                                    "Net Meter Reading": {
                                                        "title": "Net Meter Reading",
                                                        "description": "Identify the Net Meter Reading",
                                                        "type": "string"
                                                    },
                                                    "Rate 1": {
                                                        "title": "Rate 1",
                                                        "description": "Identify the Rate 1",
                                                        "type": "string"
                                                    },
                                                    "Usage 1": {
                                                        "title": "Usage 1",
                                                        "description": "Identify the Usage 1",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 1": {
                                                        "title": "Usage Cost 1",
                                                        "description": "Identify the Usage Cost 1",
                                                        "type": "string"
                                                    },
                                                    "Rate 2": {
                                                        "title": "Rate 2",
                                                        "description": "Identify the Rate 2",
                                                        "type": "string"
                                                    },
                                                    "Usage 2": {
                                                        "title": "Usage 2",
                                                        "description": "Identify the Usage 2",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 2": {
                                                        "title": "Usage Cost 2",
                                                        "description": "Identify the Usage Cost 2",
                                                        "type": "string"
                                                    },
                                                    "Rate 3": {
                                                        "title": "Rate 3",
                                                        "description": "Identify the Rate 3",
                                                        "type": "string"
                                                    },
                                                    "Usage 3": {
                                                        "title": "Usage 3",
                                                        "description": "Identify the Usage 3",
                                                        "type": "string"
                                                    },
                                                    "Usage Cost 3": {
                                                        "title": "Usage Cost 3",
                                                        "description": "Identify the Usage Cost 3",
                                                        "type": "string"
                                                    },
                                                    "Total Usage": {
                                                        "title": "Total Usage",
                                                        "description": "Identify the Total Usage",
                                                        "type": "string"
                                                    },
                                                    "Other Water Charges": {
                                                        "title": "Other Water Charges",
                                                        "description": "Identify the Other Water Charges",
                                                        "type": "string"
                                                    },
                                                    "Other Water Credits": {
                                                        "title": "Other Water Credits",
                                                        "description": "Identify the Other Water Credits",
                                                        "type": "string"
                                                    },
                                                    "Total Charge": {
                                                        "title": "Total Charge",
                                                        "description": "Identify the Total Charge",
                                                        "type": "string"
                                                    }
                                                },
                                                "required": ["Reading From (Date)", "Total Charge"]
                                            }
                                        }
                                    },
                                    "required": ["Vendor No.", "Vendor Name", "Account No.", "Property Address", "Posted Purchase Invoice", "Invoice Date", "Fixed Charge Start Date", "Fixed Charge End Date", "Fixed Charge for Water Service", "Fixed Charge for Waste Water", "Total Fixed Charges"]
                                }
