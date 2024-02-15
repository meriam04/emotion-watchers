import face
import pupil

def get_data():
    # TODO once data is synchronized
    return

if __name__ == "__main__":
    # This code is not done yet and is not intended to work
    # It just gives a general overview of what the fusion model should do

    test_set = get_data()

    num_classes = 2
    face_epoch = 9
    pupil_epoch = 3

    face_model = face.create_model(num_classes)
    pupil_model = pupil.create_model(num_classes)

    face_model.load_weights(face.CHECKPOINT_PATH.format(face_epoch))
    pupil_model.load_weights(pupil.CHECKPOINT_PATH.format(pupil_epoch))

    correct = 0
    for face_image, pupil_window, label in test_set:
        face_prediction = face_model.predict(face_image)
        pupil_prediction = pupil_model.predict(pupil_window)

        if max(face_prediction + pupil_prediction) == label:
            correct += 1
    
    print(f"Test accuracy: {correct/len(test_set)}")
