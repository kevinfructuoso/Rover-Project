import numpy as np

#make decisions based on Rover info
def decision_step(Rover):
    #if set into turning mode - turns a fixed 60 degrees in either direction and then tries to resume normal driving
    print(Rover.mode)
    if Rover.mode == 'turning around':

        #turn 60 degrees and then reassess
        if ((360 + Rover.yaw - Rover.turn_start_yaw) % 360 >= 60):
            Rover.mode = 'stop'
            return Rover

        #or keep turning
        else:
            Rover.throttle = 0
            Rover.steer = Rover.turn_steer
            Rover.brake = 0
            # print(Rover.mode)
            return Rover

    #determine if rover appears to be stuck (no motion)
    if abs(Rover.vel) <= 0.1:
        #increment counter
        Rover.stalled_counter += 1
        # print(Rover.stalled_counter)

        #if enough time in this condition passes
        if Rover.stalled_counter > 600:
            #start turning around and set proper variables
            Rover.mode = 'turning around'
            Rover.turn_start_yaw = Rover.yaw
            Rover.throttle = 0
            Rover.brake = 0
            turn_steer_direction(Rover, Rover.nav_angles)
            return Rover

    else:
        #reset counter
        Rover.stalled_counter = 0

    #determine if rover appears to be tilted
    if (((180 - abs(Rover.roll - 180)) >= 3) or ((180 - abs(Rover.pitch - 180)) >= 3)) and abs(Rover.vel) <= 0.1:
        Rover.tilted_counter += 1
        # print(Rover.tilted_counter)

        #if enough time in this condition passes
        if Rover.tilted_counter > 600:
            #start turning around and set proper variables
            Rover.mode = 'turning around'
            Rover.turn_start_yaw = Rover.yaw
            Rover.throttle = 0
            Rover.brake = 0
            turn_steer_direction(Rover, Rover.nav_angles)
            return Rover

    else:
        #reset counter
        Rover.tilted_counter = 0

    # Check if we have vision data to make decisions with or a sample is in view
    if len(Rover.nav_angles) > 0 or Rover.sample_in_view:

        #if a sample is in view
        if Rover.sample_in_view:
            #if need to move closer

            if np.mean(Rover.nav_dists) > 10:

                #if not moving or moving less than top allowed speed, speed up
                if 0 <= Rover.vel < (0.05*np.mean(Rover.nav_dists) - 0.5):
                    Rover.brake = 0
                    Rover.throttle = Rover.throttle_set
                    Rover.mode = 'forward'

                #if moving above max speed or backwards, brake
                else:
                    Rover.throttle = 0
                    Rover.brake = np.clip(((1 - 0.005*np.mean(Rover.nav_dists)) *Rover.brake_set),0,Rover.brake_set)

                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)

            #if we are close enough to pick up, stop and wait to pick up
            elif Rover.sample_in_view and Rover.near_sample:
                Rover.steer = 0
                Rover.brake = Rover.brake_set
                Rover.throttle = 0
                Rover.mode = 'stop'

        #if sample is not in view, continue normal driving
        else:

            # Check for Rover.mode status
            if Rover.mode == 'forward': 

                # Check the extent of navigable terrain
                if len(Rover.nav_angles) >= Rover.stop_forward:  

                    # If mode is forward, navigable terrain looks good and velocity is below max, then throttle 
                    if Rover.vel < Rover.max_vel:
                        # Set throttle value to throttle setting
                        Rover.throttle = Rover.throttle_set

                    else: # Else coast
                        Rover.throttle = 0

                    Rover.brake = 0
                    # Set steering to average angle clipped to the range +/- (5 to 8.5)
                    if np.mean(Rover.nav_angles * 180/np.pi) >= 0:
                        Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), 5, 8.5)

                    else:
                        Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -5, -8.5)

                # If there's a lack of navigable terrain pixels then go to 'stop' mode
                elif len(Rover.nav_angles) < Rover.stop_forward:
                        # Set mode to "stop" and hit the brakes!
                        Rover.throttle = 0
                        # Set brake to stored brake value
                        Rover.brake = Rover.brake_set
                        Rover.steer = 0
                        Rover.mode = 'stop'

            # If we're already in "stop" mode then make different decisions
            elif Rover.mode == 'stop':

                # If we're in stop mode but still moving keep braking
                if Rover.vel > 0.2:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0

                # If we're not moving
                elif Rover.vel <= 0.2:

                    # Now we're stopped and we have vision data to see if there's a path forward
                    if len(Rover.nav_angles) < Rover.go_forward:
                        Rover.throttle = 0

                        #determine which direction is smarter to turn if we cannot go forward
                        if np.mean(Rover.nav_angles) <= 0:
                            Rover.mode = 'right'

                        else:
                            Rover.mode = 'left'

                    # If we're stopped but see sufficient navigable terrain in front then go!
                    if abs(np.mean(Rover.nav_angles * 180/np.pi)) < 5 and len(Rover.nav_angles) >= Rover.go_forward: #np.mean(Rover.nav_dists) 
                        # Set throttle back to stored value
                        Rover.throttle = Rover.throttle_set
                        # Set steer to mean angle
                        Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -8.5, 8.5)
                        Rover.mode = 'forward'

                    # Release the brake to allow turning
                    Rover.brake = 0

            #if we need to turn right, continue turning until the mean angle is straight forward within 5 degrees 
            elif Rover.mode == 'right':

                if len(Rover.nav_angles) < Rover.go_forward or abs(np.mean(Rover.nav_angles * 180/np.pi)) > 5:
                    Rover.steer = -15

                else:
                    Rover.mode = 'forward'

            #if we need to turn left, continue turning until the mean angle is straight forward within 5 degrees
            elif Rover.mode == 'left':

                if len(Rover.nav_angles) < Rover.go_forward or abs(np.mean(Rover.nav_angles * 180/np.pi)) > 5:
                    Rover.steer = 15

                else:
                    Rover.mode = 'forward' 

    #if no sample is in view and there is no navigable terrain e.g. staring straight at a wall
    #set to turn around by fixed 60 degree increments
    else:
        Rover.throttle = 0
        turn_steer_direction(Rover,Rover.nav_angles)
        Rover.turn_start_yaw = Rover.yaw
        # Rover.brake = Rover.brake_set
        Rover.mode = 'turning around'

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    # print(Rover.mode)
    return Rover

#helper function to determine which direction to turn if rover got stuck
def turn_steer_direction(Rover, angles):
    if len(angles) > 0 and np.mean(angles) >= 0:
        Rover.turn_steer = 15
    elif len(angles) > 0 and np.mean(angles) < 0:
        Rover.turn_steer = -15
    else:
        Rover.turn_steer = 15