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
        
             
        #Set Orders Number like that so the Optimal solution can be derived . a little manipulation of data 
        if self.MaxRiders > 0:
            minCapacity = self.RiderCapacity
        elif self.MaxCabs > 0:
            minCapacity = self.CabCapacity
        else:
            return "No Result Possible with this Data !"
        
        remainder = self.TotalHubOrders % minCapacity
        remainder = minCapacity - remainder if remainder > 0 else 0
        
        prob = LpProblem("The Whiskas Problem",LpMinimize)
        
        x1=LpVariable("Rider",0,None,cat=pulp.LpInteger)
        x2=LpVariable("Cab",0,None,cat=pulp.LpInteger)
        
        # defines the constraints
        prob += self.RiderCapacity*x1+self.CabCapacity*x2 == self.TotalHubOrders + remainder
        prob += x1+x2 <= self.MaxRiders + self.MaxCabs
        prob += x1<= self.MaxRiders
        prob += x2<= self.MaxCabs
        prob += x1>=0
        prob += x2>=0
        
        prob += self.CostRider*self.DistanceToCover*x1 + self.CostCab*self.DistanceToCover*x2, "Total Cost of fuel / km"
        
        
        prob.solve()
        
        
        #print("Status:", LpStatus[prob.status])
        
        for v in prob.variables():
            print(v.name, "=", v.varValue)
            
            
        #print("Total Rider & Cab Cost = ", value(prob.objective))
        
        dictObj = {"Hub Name" : self.HubName , 
                   'Riders' : prob.variables()[1].varValue,'Cabs' : prob.variables()[0].varValue,
                   'Total Cost' : str(value(prob.objective)), 
                   'Solution Status' : LpStatus[prob.status],
                   "Un-Used Capacity" : str(remainder)}
                   
        return dictObj