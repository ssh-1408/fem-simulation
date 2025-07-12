from rest_framework import serializers

class BoundaryTempsSerializer(serializers.Serializer):
    top = serializers.FloatField()
    bottom = serializers.FloatField()
    left = serializers.FloatField()
    right = serializers.FloatField()

class InitialGridRequestSerializer(serializers.Serializer):
    widthNumber = serializers.IntegerField()
    heightNumber = serializers.IntegerField()
    physicalWidth = serializers.FloatField()
    physicalHeight = serializers.FloatField()
    boundaryTemps = BoundaryTempsSerializer()

class GridEvolutionRequestSerializer(InitialGridRequestSerializer):
    alpha = serializers.FloatField()
    dt = serializers.FloatField()
    steps = serializers.IntegerField()
