import os
#os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import tensorflow as tf
import numpy as np
import cv2
from utils import cpm_utils, tf_utils
from cpm_net import *

# In[2]:


tfr_data_files = ['alg2.tfrecords','alg3_iter2.tfrecords']
input_size = 368
heatmap_size = 46
stages =6 
center_radius =30 
num_of_joints = 19
batch_size = 30
training_iterations = 999999
lr =0.0001
lr_decay_rate = 0.9 
lr_decay_step =500
color_channel ='RGB'



# In[3]:


batch_x, batch_y = tf_utils.read_batch_cpm(tfr_data_files, input_size, heatmap_size, num_of_joints, batch_size)


# In[4]:


input_placeholder = tf.placeholder(dtype=tf.float32, shape=(batch_size, input_size, input_size, 3),name='input_placeholer')


# In[5]:


cmap_placeholder = tf.placeholder(dtype=tf.float32, shape=(batch_size, input_size, input_size, 1),
                                      name='cmap_placeholder')
hmap_placeholder = tf.placeholder(dtype=tf.float32,shape=(batch_size, heatmap_size,heatmap_size,num_of_joints + 1),
                                      name='hmap_placeholder')


# In[6]:


model = CPM_Model(stages, num_of_joints + 1)


# In[ ]:


model.build_model(input_placeholder, batch_size)
model.build_loss(hmap_placeholder, lr, lr_decay_rate, lr_decay_step)


# In[ ]:

with tf.Session() as sess:

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)


    saver = tf.train.Saver(var_list=tf.trainable_variables())

    init = tf.global_variables_initializer()
    
    sess.run(init)
    saver.restore(sess,"alg3_iter1.ckpt-1625")

    '''
    model.load_weights_from_file(pretrained_model, sess, finetune=True)

    for variable in tf.trainable_variables():
        with tf.variable_scope('', reuse=True):
                var = tf.get_variable(variable.name.split(':0')[0])
                print(variable.name, np.mean(sess.run(var)))           
    '''
    for i in range(0, training_iterations + 1):
        # Read in batch data
        batch_x_np, batch_y_np = sess.run([batch_x,batch_y])
 
        # Recreate heatmaps
        #gt_heatmap_np = cpm_utils.make_gaussian_batch(batch_y_np, heatmap_size, 2)

        # Update once
        stage_losses_np, total_loss_np, _, summary, current_lr, \
        stage_heatmap_np, global_step = sess.run([model.stage_loss,
                                                      model.total_loss,
                                                      model.train_op,
                                                      model.merged_summary,
                                                      model.lr,
                                                      model.stage_heatmap,
                                                      model.global_step
                                                      ],
                                                     feed_dict={input_placeholder: batch_x_np,
                                                                hmap_placeholder: batch_y_np})

        print(global_step)   
        print(total_loss_np)
        #mem = sess.run(tf.contrib.memory_stats.MaxBytesInUse())
        #print(mem)
        if global_step % 2000 == 0:
            saver.save(sess=sess, save_path="./alg3_iter2.ckpt", global_step=global_step)
            print('\nModel checkpoint saved...\n')

            
        if total_loss_np <= 50:
            saver.save(sess=sess, save_path="./alg3_iter2.ckpt", global_step=global_step)
            print('\nModel checkpoint saved...\n')
            break


    coord.request_stop()
    coord.join(threads)


print('Training done.')
        
                
                
                
                
                
                