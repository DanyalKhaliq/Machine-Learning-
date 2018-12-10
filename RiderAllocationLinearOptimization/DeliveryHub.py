from pulp import *

class DeliveryHub:
    def  __init__(self,HubName,MaxRiders,MaxCabs,RiderCapacity,
                  CabCapacity,CostRider,CostCab,DistanceToCover,TotalHubOrders):
        self.HubName = HubName
        self.MaxRiders = MaxRiders
        self.MaxCabs = MaxCabs
        self.RiderCapacity = RiderCapacity
        self.CabCapacity = CabCapacity
        self.CostRider = CostRider
        self.CostCab = CostCab
        self.DistanceToCover = DistanceToCover
        self.TotalHubOrders = TotalHubOrders
        
    def CalculateOptimizedSolution(self):
        
             
        prob = LpProblem("The Whiskas Problem",LpMinimize)
        
        x1=LpVariable("Rider",0,None,cat=pulp.LpInteger)
        x2=LpVariable("Cab",0,None,cat=pulp.LpInteger)
        
        # defines the constraints
        prob += self.RiderCapacity*x1+self.CabCapacity*x2 == self.TotalHubOrders
        prob += x1+x2 <= self.MaxRiders + self.MaxCabs
        prob += x1<= self.MaxRiders
        prob += x2<= self.MaxCabs
        prob += x1>=0
        prob += x2>=0
        
        prob += 2.5*self.DistanceToCover*x1 + 10*self.DistanceToCover*x2, "Total Cost of fuel / km"
        
        
        prob.solve()
        
        
        #print("Status:", LpStatus[prob.status])
        
        for v in prob.variables():
            print(v.name, "=", v.varValue)
            
            
        #print("Total Rider & Cab Cost = ", value(prob.objective))
        
        dictObj = {"Hub Name" : self.HubName , 
                   'Riders' : prob.variables()[1].varValue,'Cabs' : prob.variables()[0].varValue,
                   'Total Rider & Cab Cost' : str(value(prob.objective)), 
                   'Solution Status' : LpStatus[prob.status],
                   "Total Deliverable Capacity by selected Combination" : str(prob.variables()[1].varValue*self.RiderCapacity + prob.variables()[0].varValue*self.CabCapacity)}
                   
        return dictObj