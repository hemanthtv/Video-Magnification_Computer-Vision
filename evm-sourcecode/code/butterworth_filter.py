#..................................
#........Visualisierung 2..........
#..................................
#...Eulerian Video Magnification...
#..................................
#.. Author: Galya Pavlova..........
#..................................

from scipy.signal import butter, lfilter

import pyramid
import video


def butter_bandpass(lowcut, highcut, fs, order=1):
    '''
    Calculates the Butterworth bandpass filter
    :param lowcut: low frequency cutoff
    :param highcut: high frequency cutoff
    :param fs: video frame rate
    :param order: filter order - per default = 1
    :return: Numerator (b) and denominator (a) polynomials of the IIR filter.
    '''

    low = lowcut / fs
    high = highcut / fs
    b, a = butter(order, [low, high], btype='band')
    return b, a


def apply_butter(laplace_video_list, levels, alpha, cutoff, low, high, fps, width, height, linearAttenuation):
    '''
    Applies the Butterworth filter on video sequence, magnifies the filtered video sequence
    and cuts off spatial frequencies
    :param laplace_video_list: Laplace video pyramid
    :param levels: Pyramid levels
    :param alpha: Magnification factor
    :param cutoff: Spatial frequencies cutoff factor
    :param low: Temporal low frequency cutoff
    :param high: Temporal high frequency cutoff
    :param fps: Video frame rate
    :param width: Video frame width
    :param height: Video frame height
    :param linearAttenuation: Boolean if linear attenuation should be applied
    :return:
    '''

    print('Apply Butterworth filter')
    filtered_video_list = []
    b, a = butter_bandpass(low, high, fps, order=1)

    # spacial wavelength lambda
    lambda1 = (width ** 2 + height ** 2) ** 0.5

    delta = cutoff / 8 / (1 + alpha)

    for i in range(levels):  # pyramid levels

        current_alpha = lambda1 / 8 / delta - 1  # given in paper
        current_alpha /= 2

        # apply the butterworth filter onto temporal image sequence
        filtered = lfilter(b, a, laplace_video_list[i], axis=0)

        if i == levels - 1 or i == 0:  # ignore lowest and highest level
            filtered *= 0

        # spacial frequencies attenuation
        if current_alpha > alpha:
            filtered *= alpha
        else:
            if linearAttenuation:
                filtered *= current_alpha
            else:
                filtered *= 0

        filtered_video_list.append(filtered)

        lambda1 /= 2

    return filtered_video_list


def start(vidFile, alpha, cutoff, low, high, linearAttenuation, chromAttenuation, name):
    '''
    Performs motion magnification on the video by applying Butterworth bandpass filter and saves the output video
    :param vidFile: Video file
    :param alpha: Magnification factor
    :param cutoff: Spatial frequencies cutoff factor
    :param low: Temporal low frequency cutoff
    :param high: Temporal high frequency cutoff
    :param linearAttenuation: Boolean if linear attenuation should be applied
    :param chromAttenuation: Boolean if chrominance attenuation should be applied
    :param name: Output video name
    '''
    t, fps, width, height = video.load_video(vidFile)

    #  from rgb to yiq
    t = video.rgb2yiq(t)

    levels = video.calculate_pyramid_levels(width, height)

    # build laplace pyramid for each video frame
    lap_video_list = pyramid.laplacian_video_pyramid(t, levels)

    # apply butterworth filter
    filtered_video_list = apply_butter(lap_video_list, levels, alpha, cutoff, low, high, fps, width, height, linearAttenuation)

    final = pyramid.reconstruct(filtered_video_list, levels)

    # chromatic attenuation
    final[:][:][:][1] *= chromAttenuation
    final[:][:][:][2] *= chromAttenuation

    # Add to original
    final += t

    # from yiq to rgb
    final = video.yiq2rgb(final)

    # Cutoff wrong values
    final[final < 0] = 0
    final[final > 255] = 255

    video.save_video(final, fps, name)

    print('Finished')
