
from model_pool.utils import *
import torch.optim.lr_scheduler as lr_scheduler
import SimpleITK as sitk





class BaseModel():
    def name(self):
        return 'BaseModel'

    def initialize(self, opt):
        self.opt = opt
        self.gpu_ids = opt['tsk_set']['gpu_ids']
        self.isTrain = opt['tsk_set']['train']
        self.save_dir = opt['tsk_set']['path']['check_point_path']
        self.record_path = opt['tsk_set']['path']['record_path']
        self.img_sz = opt['tsk_set']['img_size']
        self.spacing = None
        self.continue_train = opt['tsk_set']['continue_train']
        self.criticUpdates = opt['tsk_set']['criticUpdates']
        self.n_in_channel = opt['tsk_set']['n_in_channel']
        self.input_resize_factor = opt['tsk_set']['input_resize_factor']
        self.optimizer= None
        self.lr_scheduler = None
        self.exp_lr_scheduler= None
        self.iter_count = 0
        self.dim = len(self.img_sz)
        self.network =None
        self.val_res_dic = {}
        self.fname_list = None
        self.moving = None
        self.target = None
        self.output = None





    def set_input(self, input):
        self.input = input

    def forward(self,input):
        pass

    def test(self):
        pass

    def set_train(self):
        self.network.train(True)
        self.is_train =True
    def set_val(self):
        self.network.train(False)
        self.is_train = False

    def set_debug(self):
        self.network.train(False)
        self.is_train = False

    def set_test(self):
        self.network.train(False)
        self.is_train = False



    def optimize_parameters(self):
        pass

    def init_optim(self, opt,network, warmming_up = False):
        optimize_name = opt['optim_type']
        if not warmming_up:
            lr = opt['lr']
            print(" no warming up the learning rate is {}".format(lr))
        else:
            lr = 1e-4
            print(" warming up on the learning rate is {}".format(lr))
        beta = opt['adam']['beta']
        lr_sched_opt = opt['lr_scheduler']
        self.lr_sched_type = lr_sched_opt['type']
        if optimize_name == 'adam':
            re_optimizer = torch.optim.Adam(network.parameters(), lr=lr, betas=(beta, 0.999))
        else:
            re_optimizer = torch.optim.SGD(network.parameters(), lr=lr)
        re_optimizer.zero_grad()
        re_lr_scheduler = None
        re_exp_lr_scheduler = None
        if self.lr_sched_type == 'custom':
            step_size = lr_sched_opt['custom']['step_size']
            gamma = lr_sched_opt['custom']['gamma']
            re_lr_scheduler = torch.optim.lr_scheduler.StepLR(re_optimizer, step_size=step_size, gamma=gamma)
        elif self.lr_sched_type == 'plateau':
            patience = lr_sched_opt['plateau']['patience']
            factor = lr_sched_opt['plateau']['factor']
            threshold = lr_sched_opt['plateau']['threshold']
            min_lr = lr_sched_opt['plateau']['min_lr']
            re_exp_lr_scheduler = lr_scheduler.ReduceLROnPlateau(re_optimizer, mode='min', patience=patience,
                                                                   factor=factor, verbose=True,
                                                                   threshold=threshold, min_lr=min_lr)
        return re_optimizer,re_lr_scheduler,re_exp_lr_scheduler




    # get image paths
    def get_image_paths(self):
        return self.fname_list


    def set_cur_epoch(self,epoch):
        self.cur_epoch = epoch
        self.cur_epoch_beg_tag = True


    def backward_net(self):
        self.loss.backward()


    def cal_loss(self,output= None):
       pass


    def get_current_errors(self):
        return self.loss.data[0]



    def compute_jacobi_map(self,map):
        pass




    def cal_val_errors(self, split_size=2):
        self.cal_test_errors(split_size)

    def cal_test_errors(self,split_size=2):
       pass


    def update_loss(self, epoch, end_of_epoch):
        pass

    def get_val_res(self, detail=False):
        if len(self.val_res_dic):
            if not detail:
                return np.mean(self.val_res_dic['batch_avg_res']['dice'][0, 1:]), self.val_res_dic['batch_avg_res'][
                    'dice']
            else:
                return np.mean(self.val_res_dic['batch_avg_res']['dice'][0, 1:]), self.val_res_dic['multi_metric_res']
        else:
            return -1, np.array([-1, -1])


    def get_test_res(self, detail=False):
        return self.get_val_res(detail = detail)

    def get_extra_res(self):
        return None


    def save_fig(self,phase,standard_record=False,saving_gt=True):
       pass


    def check_and_update_model(self,epoch):
        return None


    def do_some_clean(self):
        self.loss = None
        self.gt = None
        self.input = None
        self.output = None


    def save_fig_3D(self,phase):
        saving_folder_path = os.path.join(self.record_path, '3D')
        make_dir(saving_folder_path)
        for i in range(self.moving.size(0)):
            appendix = self.fname_list[i] + "_"+phase+ "_iter_" + str(self.iter_count)
            saving_file_path = saving_folder_path + '/' + appendix + "_moving.nii.gz"
            output = sitk.GetImageFromArray(self.moving[i, 0, ...])
            output.SetSpacing(self.spacing)
            sitk.WriteImage(output, saving_file_path)
            saving_file_path = saving_folder_path + '/' + appendix + "_target.nii.gz"
            output = sitk.GetImageFromArray(self.target[i, 0, ...])
            output.SetSpacing(self.spacing)
            sitk.WriteImage(output, saving_file_path)
            saving_file_path = saving_folder_path + '/' + appendix + "_warped.nii.gz"
            output = sitk.GetImageFromArray(self.output[i, 0, ...])
            output.SetSpacing(self.spacing)
            sitk.WriteImage(output, saving_file_path)










