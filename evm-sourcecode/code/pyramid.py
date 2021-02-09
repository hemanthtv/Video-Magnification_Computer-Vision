#..................................
#........Visualisierung 2..........
#..................................
#...Eulerian Video Magnification...
#..................................
#.. Author: Galya Pavlova..........
#..................................

import cv2
import numpy as np


def create_gaussian_pyramid(image, levels):
    '''
    Creates a Gaussian pyramid for each image.
    :param image: An image, i.e video frame
    :param levels: The Gaussian pyramid level
    :return: Returns a pyramid of nr. levels images
    '''
    gauss = image.copy()
    gauss_pyr = [gauss]

    for level in range(1, levels):
        gauss = cv2.pyrDown(gauss)
        gauss_pyr.append(gauss)

    return gauss_pyr


def gaussian_video(video_tensor, levels):
    '''
    For a given video sequence the function creates a video with
    the highest (specified by levels) Gaussian pyramid level
    :param video_tensor: Video sequence
    :param levels: Specifies the Gaussian pyramid levels
    :return: a video sequence where each frame is the downsampled of the original frame
    '''
    for i in range(0, video_tensor.shape[0]):
        frame = video_tensor[i]
        pyr = create_gaussian_pyramid(frame, levels)
        gaussian_frame = pyr[-1]  # use only highest gaussian level
        if i == 0:                # initialize one time
            vid_data = np.zeros((video_tensor.shape[0], gaussian_frame.shape[0], gaussian_frame.shape[1], 3))

        vid_data[i] = gaussian_frame
    return vid_data


def create_laplacian_pyramid(image, levels):
    '''
    Builds a Laplace pyramid for an image, i.e. video frame
    :param image: Image,  i.e. single video frame
    :param levels: Specifies the Laplace pyramid levels
    :return: Returns a pyramid of nr. levels images
    '''
    gauss_pyramid = create_gaussian_pyramid(image, levels)
    laplace_pyramid = []
    for i in range(levels-1):
        size = (gauss_pyramid[i].shape[1], gauss_pyramid[i].shape[0])  # reshape
        laplace_pyramid.append(gauss_pyramid[i]-cv2.pyrUp(gauss_pyramid[i+1], dstsize=size))

    laplace_pyramid.append(gauss_pyramid[-1])  # add last gauss pyramid level
    return laplace_pyramid


def laplacian_video_pyramid(video_stack, levels):
    '''
    Creates a Laplacian pyramid for the whole video sequence
    :param video_stack: Video sequence
    :param levels: Specifies the Laplace pyramid levels
    :return: A two-dimensional array where the first index is used for the pyramid levels
    and the second for each video frame
    '''
    print('Build laplace pyramid')

    # "2 dimensional" array - first index for pyramid level, second for frames
    laplace_video_pyramid = [[0 for x in range(video_stack.shape[0])] for x in range(levels)]

    for i in range(video_stack.shape[0]):
        frame = video_stack[i]
        pyr = create_laplacian_pyramid(frame, levels)

        for n in range(levels):
            laplace_video_pyramid[n][i] = pyr[n]

    return laplace_video_pyramid


def reconstruct(filtered_video, levels):
    '''
    Reconstructs a video sequence from the filtered Laplace video pyramid
    :param filtered_video: 2 dimensional video sequence - 1st. index pyramid levels, 2nd. - video frames
    :param levels: pyramid levels
    :return: video sequence
    '''
    print('Reconstruct video')

    final = np.empty(filtered_video[0].shape)
    for i in range(filtered_video[0].shape[0]):  # iterate through frames

        up = filtered_video[-1][i]         # highest level
        for k in range(levels-1, 0, -1):       # going down to lowest level
            size = (filtered_video[k-1][i].shape[1], filtered_video[k-1][i].shape[0])  # reshape
            up = cv2.pyrUp(up, dstsize=size) + filtered_video[k-1][i]

        final[i] = up

    return final
