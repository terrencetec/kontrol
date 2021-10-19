# """Composite model class for a combination of Model objects."""
# from .model import Model


# class CompositeModel(Model):
#     """
#     """
#     def __init__(self, model1, model2, split_index, operator):
#         """Constructor
        
#         Parameters
#         ----------
#         model1 : kontrol.curvefit.model.Model
#             The first model.
#         model2 : kontrol.curvefit.model.Model
#             The second model.
#         split_index : int
#             The index to split the model parameter array.
#         operator : str
#             The operator to combine the two models.
#             Choose from ["+", "-", "*", "/"].
#         """
#         self.model1 = model1
#         self.model2 = model2
#         self.split_index = split_index
#         self.operator = operator

#     def _x2y(self, x):
#         """
#         """

#     @property
