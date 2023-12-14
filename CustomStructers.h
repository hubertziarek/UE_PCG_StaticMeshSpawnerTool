// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "MeshSelectors/PCGMeshSelectorWeighted.h"
#include "CustomStructers.generated.h"


USTRUCT(BlueprintType)
struct FNodeToChoose
{

	GENERATED_BODY()


	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 Index;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TObjectPtr<class UPCGMeshSelectorWeighted> Reference;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString Title;

	FNodeToChoose()
	{
		Index = -1;
		Reference = nullptr;
		Title = "None";
	}

};