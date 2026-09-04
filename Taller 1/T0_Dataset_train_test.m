%% Dataset_train_test: division de Iris en entrenamiento y test
% El script de clase, con round en el corte y guardando las particiones en un .mat
clear; close all; clc

load iris.dat
No_examples = length(iris);

%% Se mezcla el dataset con una semilla fija
rng(2021)
ind = randperm(No_examples);

%% Division 60-40, 70-30, 80-20 y 90-10
proporciones = [0.6 0.7 0.8 0.9];
for k = 1:4
    n_train = round(proporciones(k) * No_examples);
    S(k).p   = proporciones(k);
    S(k).Xtr = iris(ind(1:n_train), 1:4);
    S(k).ytr = iris(ind(1:n_train), 5);
    S(k).Xte = iris(ind(n_train+1:end), 1:4);
    S(k).yte = iris(ind(n_train+1:end), 5);
end
S

%% Ejemplo: la particion 60-40 como la deja el script original
iris_train60 = [S(1).Xtr S(1).ytr];
iris_test40 = S(1).Xte;
iris_testclass40 = S(1).yte;
size(iris_train60), size(iris_test40)

save('iris_splits.mat', 'S')
