from BlockComponents.Configuration import *
from BlockComponents.Step import *
from svmutil import *

class StepLibSVM(TransformStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self.mParams = None

    def _Execute(self, **kwargs : DataMatrix):
        svm_model.predict = lambda self, x: svm_predict([0], [x], self)[0][0]

        prob = svm_problem([1, -1], [[1, 0, 1], [-1, 0, -1]])

        param = svm_parameter('-q')
        param.kernel_type = LINEAR # self.mParams['kernel_type']
        param.C = self.mParams['C']

        m = svm_train(prob, param)

        # Get the prediction values from the SVM model
        svm_type = m.get_svm_type()
        nr_class = m.get_nr_class()
        svr_probability = m.get_svr_probability()
        class_labels = m.get_labels()
        sv_indices = m.get_sv_indices()
        nr_sv = m.get_nr_sv()
        is_prob_model = m.is_probability_model()
        support_vector_coefficients = m.get_sv_coef()
        support_vectors = m.get_SV()
        print(support_vector_coefficients)
        #m.predict([1, 1, 1])
        return True

    def _SetConfiguration(self, config : ConfigBase):
        try:
            self.mParams = config.GetStepParams(self.GetStepID())
        except:
            return False
        return True

test = StepLibSVM('StepSVMTest')

config = StepConfig()
config.Read('../../config/default.yaml')

test.Configure(config)
test.Do()