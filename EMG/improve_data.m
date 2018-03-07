function [] = improve_data(fileName, time_shift)
%IMPROVE_DATA Allows to cut the beginning of a recording to sync the data

load(fileName)

% 5 second subtraction
X1 = X(512*time_shift:end, :);
force1 = force(512*time_shift:end);
clear X;
clear force;
X = X1;
force = force1;

time_stamps(1:512*time_shift) = [];

clear X1;
clear force1;

save(strcat(erase(fileName, ".mat"), "_improved.mat"));
end