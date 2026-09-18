function generar_v2
% Corre el live script de la version 2, guarda sus figuras en v2/informe/figuras
% y deja el .mlx ejecutado en v2/. Se llama desde la carpeta Taller 1.
cd v2
copyfile('../data_banknote_authentication.txt', '.');
copyfile('../iris.dat', '.');
if exist('Taller1_Perceptron_Adaline_LiveScript.mlx', 'file')
    delete('Taller1_Perceptron_Adaline_LiveScript.mlx')   % el mlx ensombrece al .m
end
correr('Taller1_Perceptron_Adaline_LiveScript.m')
figs = findobj('Type', 'figure');
[~, orden] = sort([figs.Number]);
figs = figs(orden);
if ~exist('informe/figuras', 'dir'), mkdir('informe/figuras'); end
for k = 1:numel(figs)
    figs(k).Theme = 'light';
    figs(k).Position = [50 50 760 440];
    set(findall(figs(k), '-property', 'FontSize'), 'FontSize', 13)
    exportgraphics(figs(k), fullfile('informe', 'figuras', sprintf('fig%02d.png', k)), 'Resolution', 150)
end
close all
mlx = fullfile(pwd, 'Taller1_Perceptron_Adaline_LiveScript.mlx');
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'Taller1_Perceptron_Adaline_LiveScript.m'), mlx);
matlab.internal.liveeditor.executeAndSave(mlx);
close all
cd ..
end

function correr(nombre)
% El script empieza con clear, por eso corre en su propio espacio de trabajo
run(nombre);
end
