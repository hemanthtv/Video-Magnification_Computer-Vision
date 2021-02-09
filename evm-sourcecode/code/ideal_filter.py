#..................................
#........Visualisierung 2..........
#..................................
#...Eulerian Video Magnification...
#..................................
#.. Author: Galya Pavlova..........
#..................................

import scipy.fftpack as fftpack
import numpy as np
import cv2

import pyramid
import video


def start(vidFile, alpha, low, high, chromAttenuation, name):
    '''
    Performs color magnification on the video by applying an ideal bandpass filter,
    i.e. applies a discrete fourier transform on the gaussian downsapled video and
    cuts off the frequencies outside the bandpass filter, magnifies the result and
    saves the output video
    :param vidFile: Video file
    :param alpha: Magnification factor
    :param low: Temporal low frequency cutoff
    :param high: Temporal high frequency cutoff
    :param chromAttenuation: Boolean if chrominance attenuation should be applied
    :param name: Output video name
    '''

    t, fps, width, height = video.load_video(vidFile)

    #  from rgb to yiq
    t = video.rgb2yiq(t)

    levels = 5

    # build Gaussian pyramid and use the highest level
    gauss_video_list = pyramid.gaussian_video(t, levels)

    print('Apply Ideal filter')
    # apply discrete fourier transformation (real)
    fft = fftpack.rfft(gauss_video_list, axis=0)
    frequencies = fftpack.rfftfreq(fft.shape[0], d=1.0 / fps)  # sample frequencies
    mask = np.logical_and(frequencies > low, frequencies < high)  # logical array if values between low and high frequencies

    fft[~mask] = 0                # cutoff values outside the bandpass

    filtered = fftpack.irfft(fft, axis=0)   # inverse fourier transformation

    filtered *= alpha  # magnification

    # chromatic attenuation
    filtered[:][:][:][1] *= chromAttenuation
    filtered[:][:][:][2] *= chromAttenuation

    # resize last gaussian level to the frames size
    filtered_video_list = np.zeros(t.shape)
    for i in range(t.shape[0]):
        f = filtered[i]
        filtered_video_list[i] = cv2.resize(f, (t.shape[2], t.shape[1]))

    final = filtered_video_list

    # Add to original
    final += t

    # from yiq to rgb
    final = video.yiq2rgb(final)

    # Cutoff wrong values
    final[final < 0] = 0
    final[final > 255] = 255

    video.save_video(final, fps, name)

    print('Finished')
