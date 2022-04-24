package com.example.saccbackend3.service.Impl;

import com.example.saccbackend3.entity.Student;
import com.example.saccbackend3.mapper.StudentMapper;
import com.example.saccbackend3.service.StudentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 *
 * @author TX
 * @date 2022/3/24 12:43
 */
@Service
public class StudentServiceImpl implements StudentService {

    @Autowired
    private StudentMapper studentMapper;


    @Override
    public Boolean addStudent(Student student) {
        if (studentMapper.addStudent(student) > 0)
            return true;
        else
            return false;
    }

    @Override
    public Boolean deleteStudentById(String id) {
        int i = studentMapper.deleteStudentById(id);
        if (i > 0)
            return true;
        else
            return false;
    }

    @Override
    public Boolean updateStudent(Student student) {
        int i = studentMapper.updateStudent(student);
        if (i > 0)
            return true;
        else
            return false;
    }

    @Override
    public List<Student> listStudent() {
        return studentMapper.listStudent();
    }

    @Override
    public List<Student> listStudentByAges(Integer age1, Integer age2) {
        return studentMapper.listStudentByAges(age1, age2);
    }
}
