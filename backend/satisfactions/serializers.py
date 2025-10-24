from rest_framework import serializers
from langdetect import detect
import joblib
import os
from .models import Satisfaction


class SatisfactionSerializer(serializers.ModelSerializer):
    """
    Serializer to convert Satisfaction objects to JSON.
    Custom validations for fields.
    """

    class Meta:
        model = Satisfaction
        fields = ["email", "last_name", "first_name", "description", "polarity", "user"]
        extra_kwargs = {"user": {"read_only": True}, "polarity": {"read_only": True},}

    def validate_email(self, value):
        """
        Ensures that the email is not empty or composed only of spaces.
        """
        if not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        return value

    def validate_description(self, value):
        """
        Ensures that the description is not empty or composed only of spaces.
        Ensures that the description has at least 10 characters.
        """
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        elif len(value) < 10:
            raise serializers.ValidationError(
                "The description must contain at least 10 characters."
            )
        return value

    def validate(self, data):
        """
            Checks if satisfaction comment is written in french or english.
            and add polarity to guess if it is positive or negative
            Otherwise raise an error.
        """
        lang_available = ['fr', 'en']
        msg = data['description']

        lang_detected = detect(msg)

        if lang_detected not in lang_available:
            raise serializers.ValidationError(
                "Input of satisfaction commentary should be written in French or English"
            )
        
        data_path = os.getenv("DATA_PATH")

        if lang_detected == 'fr':
            if not os.path.isfile(data_path + "model_ia_fr.pkl"):
                raise serializers.ValidationError(
                    "Sorry we can not know if your comment is positive or negative."
                )
    
            model = joblib.load(data_path + "./model_ia_fr.pkl")

        if lang_detected == 'en':
            if not os.path.isfile(data_path + "./model_ia_en.pkl"):
                raise serializers.ValidationError(
                    "Sorry we can not know if your comment is positive or negative."
                )
        
            model = joblib.load(data_path + "./model_ia_en.pkl")

        prediction = model.predict([msg.lower()])

        data['polarity'] = True if prediction[0] == 1 else False
        return data 
