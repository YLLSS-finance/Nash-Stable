# Nash methods 

This Document aims to be an explicit explanation of all functions in the Nash class, the main class of the Nash exchange.

# **Initialisation**
The Nash exchange class, at its basic level, stores data pertaining to the following:
 - Trading Account objects, keyed by Market Participant ID (self.accounts);
 - Order Book objects, keyed by Contract ID (self.orderBooks);
 - Contract Holder stores, keyed by Contract ID, containing one Python set per key, containing all MPIDs of people who have traded that contract;
 - An Order object, efficiently storing all orders in an efficient block of memory with NumPy.


# **Administrator Actions**
## **Creating an Account**
### **Arguments**
**mpid**: The Market Participant ID of the new account.

### **Procedure**
- Check if argument **mpid** is present in **self.accounts**. *If so, error*.
- If **mpid** is **not present**:  
  - Assosciate **mpid** with a new **account object**.
  - Log the new **mpid** into the **order object**.

## **Adding a Contract**
### **Arguments**
**contract_id**: An integer used to identify the new contract.

### **Procedures
- Check if argument **contract_id** is present in **self.orderBooks**. *If so, error.*
