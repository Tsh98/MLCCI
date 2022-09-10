# coding=utf-8
import os

import featureExtract
import Tool_localization

if __name__ == "__main__":
    versionPath = "D:\\CC\\1_back"
    # 四个测试用例 0 2 3通过 1未通过
    inVector = [0, 1, 0, 1]
    covMatrix = [
        [1, 0, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 1, 1],
    ]
    statement_num = len(covMatrix[0])
    case_num = len(covMatrix)
    formulaSus, ochiai = Tool_localization.statement_sus(case_num, statement_num, covMatrix, inVector)
    print(formulaSus)
    CR = featureExtract.getCoverageRatioFactor(versionPath, covMatrix, inVector, formulaSus)
    print(CR)

    SF = featureExtract.getSimilarityFactor(versionPath, covMatrix, inVector, formulaSus)
    print(SF)

    target = os.path.join(versionPath, "hugeTest.txt")
    FM = featureExtract.getFaultMaskingFactor(versionPath, covMatrix, inVector, ochiai, target)
    print(FM)