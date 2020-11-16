from typing import Optional, List, Any
from datetime import datetime


class Policy:
    DependentAnswers: Optional[List[Any]]
    Nominees: Optional[List[Any]]
    PolicyAgents: Optional[List[Any]]
    Dependents: Optional[List[Any]]
    FirstName: Optional[str]
    LastName: Optional[str]
    FatherName: Optional[str]
    CNIC: Optional[str]
    Email: Optional[str]
    CCEmail: None
    Phone: Optional[str]
    Address: Optional[str]
    City: Optional[str]
    Country: Optional[str]
    PostalCode: Optional[str]
    DateOfBirth: Optional[datetime]
    Gender: Optional[int]
    Age: Optional[int]
    MaritalStatus: Optional[int]
    Relations: Optional[int]
    CNICIssueDate: Optional[datetime]
    CNICExpiryDate: Optional[str]
    HowManyKids: None
    AgentEmail: Optional[str]
    ProductNumber: Optional[str]
    PurchasedProduct: Optional[str]
    PlanCode: Optional[str]
    CompanyName: None
    RecordFrom: Optional[int]
    PolicyStatus: Optional[int]
    RecordType: Optional[int]
    StartTime: None
    EndTime: None
    StartDate: Optional[datetime]
    FK_Country_ID: Optional[int]
    FK_City_ID: Optional[int]
    IsDeliverViaCourier: Optional[bool]
    IsDiscounted: Optional[bool]
    DiscountPercentage: Optional[int]
    DiscountAmount: Optional[int]
    FKPolicyDetailID: None
    Amount: Optional[str]
    TT: None
    AgentID: None
    FKPartnerID: None
    CBC: Optional[int]
    Deduction: Optional[int]
    FKPartnerUserID: Optional[int]
    FKPartnerBranchID: None
    CompanyID: Optional[int]
    CompanyType: Optional[int]

    def __init__(self, DependentAnswers: Optional[List[Any]], Nominees: Optional[List[Any]], PolicyAgents: Optional[List[Any]], Dependents: Optional[List[Any]], FirstName: Optional[str], LastName: Optional[str], FatherName: Optional[str], CNIC: Optional[str], Email: Optional[str], CCEmail: None, Phone: Optional[str], Address: Optional[str], City: Optional[str], Country: Optional[str], PostalCode: Optional[str], DateOfBirth: Optional[datetime], Gender: Optional[int], Age: Optional[int], MaritalStatus: Optional[int], Relations: Optional[int], CNICIssueDate: Optional[datetime], CNICExpiryDate: Optional[str], HowManyKids: None, AgentEmail: Optional[str], ProductNumber: Optional[str], PurchasedProduct: Optional[str], PlanCode: Optional[str], CompanyName: None, RecordFrom: Optional[int], PolicyStatus: Optional[int], RecordType: Optional[int], StartTime: None, EndTime: None, StartDate: Optional[datetime], FKCountryID: Optional[int], FKCityID: Optional[int], IsDeliverViaCourier: Optional[bool], IsDiscounted: Optional[bool], DiscountPercentage: Optional[int], DiscountAmount: Optional[int], FKPolicyDetailID: None, Amount: Optional[str], TT: None, AgentID: None, FKPartnerID: None, CBC: Optional[int], Deduction: Optional[int], FKPartnerUserID: Optional[int], FKPartnerBranchID: None, CompanyID: Optional[int], CompanyType: Optional[int]) -> None:
        self.DependentAnswers = DependentAnswers
        self.Nominees = Nominees
        self.PolicyAgents = PolicyAgents
        self.Dependents = Dependents
        self.FirstName = FirstName
        self.LastName = LastName
        self.FatherName = FatherName
        self.CNIC = CNIC
        self.Email = Email
        self.CCEmail = CCEmail
        self.Phone = Phone
        self.Address = Address
        self.City = City
        self.Country = Country
        self.PostalCode = PostalCode
        self.DateOfBirth = DateOfBirth
        self.Gender = Gender
        self.Age = Age
        self.MaritalStatus = MaritalStatus
        self.Relations = Relations
        self.CNICIssueDate = CNICIssueDate
        self.CNICExpiryDate = CNICExpiryDate
        self.HowManyKids = HowManyKids
        self.AgentEmail = AgentEmail
        self.ProductNumber = ProductNumber
        self.PurchasedProduct = PurchasedProduct
        self.PlanCode = PlanCode
        self.CompanyName = CompanyName
        self.RecordFrom = RecordFrom
        self.PolicyStatus = PolicyStatus
        self.RecordType = RecordType
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.StartDate = StartDate
        self.FK_Country_ID = FKCountryID
        self.FK_City_ID = FKCityID
        self.IsDeliverViaCourier = IsDeliverViaCourier
        self.IsDiscounted = IsDiscounted
        self.DiscountPercentage = DiscountPercentage
        self.DiscountAmount = DiscountAmount
        self.FKPolicyDetailID = FKPolicyDetailID
        self.Amount = Amount
        self.TT = TT
        self.AgentID = AgentID
        self.FKPartnerID = FKPartnerID
        self.CBC = CBC
        self.Deduction = Deduction
        self.FKPartnerUserID = FKPartnerUserID
        self.FKPartnerBranchID = FKPartnerBranchID
        self.CompanyID = CompanyID
        self.CompanyType = CompanyType

class PaymentDetail:
    TotalAmount: int
    PaymentStatus: Optional[str]
    ResponseCode: Optional[str]
    TransactionType: Optional[str]
    FK_PolicyDetail_ID: int
    FK_Merchant_ID: Optional[int]
    CNIC: Optional[str]

    def __init__(self, TotalAmount,FK_PolicyDetail_ID,CNIC, PaymentStatus = "0", ResponseCode = "5", TransactionType = "cc" , FK_Merchant_ID = "8"):
        self.TotalAmount =  TotalAmount
        self.FK_PolicyDetail_ID = FK_PolicyDetail_ID
        self.ResponseCode = ResponseCode
        self.FK_Merchant_ID = FK_Merchant_ID
        self.TransactionType = TransactionType
        self.PaymentStatus = PaymentStatus
        self.CNIC = CNIC


from typing import Optional, List


class IntimationDetailRequest:
    DocumentType: Optional[int]
    Attachment: Optional[str]
    FileName: Optional[str]

    def __init__(self, DocumentType: Optional[int], Attachment: Optional[str], FileName: Optional[str]) -> None:
        self.DocumentType = DocumentType
        self.Attachment = Attachment
        self.FileName = FileName


class Claim:
    Admit: Optional[str]
    Amount: Optional[str]
    CardNo: Optional[str]
    ClaimType: Optional[str]
    ConfinementFrom: Optional[str]
    ConfinementTo: Optional[str]
    Expense: Optional[str]
    FKInsuredDetailID: Optional[str]
    FKPolicyID: Optional[str]
    FKPolicyInsuredDetailID: Optional[str]
    HospitalAttended: Optional[str]
    Id: Optional[str]
    IllnessDate: Optional[str]
    InsuredName: Optional[str]
    IntimationDate: Optional[str]
    IntimationDetailRequest: Optional[List[IntimationDetailRequest]]
    IntimationMode: Optional[str]
    MedicinesPrescribed: Optional[str]
    Note: Optional[str]
    PolicyNumber: Optional[str]
    PractitionerName: Optional[str]
    ReceiptDate: Optional[str]
    ReceiptNo: Optional[str]
    RecoveryDate: Optional[str]
    RelationwithInsured: Optional[str]

    def __init__(self, Admit: Optional[str], Amount: Optional[int], CardNo: Optional[str], ClaimType: Optional[int], ConfinementFrom: Optional[str], ConfinementTo: Optional[str], Expense: Optional[str], FKInsuredDetailID: Optional[int], FKPolicyID: Optional[int], FKPolicyInsuredDetailID: Optional[int], HospitalAttended: Optional[str], Id: Optional[int], IllnessDate: Optional[str], InsuredName: Optional[str], IntimationDate: Optional[str], IntimationDetailRequest: Optional[List[IntimationDetailRequest]], IntimationMode: Optional[str], MedicinesPrescribed: Optional[str], Note: Optional[str], PolicyNumber: Optional[str], PractitionerName: Optional[str], ReceiptDate: Optional[str], ReceiptNo: Optional[str], RecoveryDate: Optional[str], RelationwithInsured: Optional[str]) -> None:
        self.Admit = Admit
        self.Amount = Amount
        self.CardNo = CardNo
        self.ClaimType = ClaimType
        self.ConfinementFrom = ConfinementFrom
        self.ConfinementTo = ConfinementTo
        self.Expense = Expense
        self.FK_InsuredDetail_ID = FKInsuredDetailID
        self.FK_Policy_ID = FKPolicyID
        self.FK_PolicyInsuredDetail_ID = FKPolicyInsuredDetailID
        self.HospitalAttended = HospitalAttended
        self.Id = Id
        self.IllnessDate = IllnessDate
        self.InsuredName = InsuredName
        self.IntimationDate = IntimationDate
        self.IntimationDetailRequest = IntimationDetailRequest
        self.IntimationMode = IntimationMode
        self.MedicinesPrescribed = MedicinesPrescribed
        self.Note = Note
        self.PolicyNumber = PolicyNumber
        self.PractitionerName = PractitionerName
        self.ReceiptDate = ReceiptDate
        self.ReceiptNo = ReceiptNo
        self.RecoveryDate = RecoveryDate
        self.RelationwithInsured = RelationwithInsured
