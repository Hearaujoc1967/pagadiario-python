<?php
class Cliente_model extends CI_Model{
	
    public function guardar_cliente($id_tipo_estado_cliente,$id_reputacion,$id_cobrador,$id_documentacion,$dni,$nombre,$nombre_negocio,$direccion,$direccion_cobro,$telf,$email,$referencia_1,$referencia_2,$archivo){
    	$data = array(
    	'id_tipo_estado_cliente' =>$id_tipo_estado_cliente,
    	'id_reputacion' =>$id_reputacion,
    	'id_cobrador'=>$id_cobrador,
        'id_documentacion'=>$id_documentacion,
    	'dni'=>$dni,
    	'nombre'=>$nombre,
    	'nombre_negocio'=>$nombre_negocio,
    	'direccion'=>$direccion,
    	'direccion_cobro'=>$direccion_cobro,
    	'telf'=>$telf,
    	'email'=>$email,
    	'referencia_1'=>$referencia_1,
    	'referencia_2'=>$referencia_2,
    	'adjunto'=>$archivo);
    	$this->db->insert('t_cliente', $data);
    }
    public function actualizar_cliente($id_cliente,$dni,$nombre,$nombre_negocio,$direccion,$direccion_cobro,$telf,$email,$referencia_1,$referencia_2){
       $data = array(
        'dni'=>$dni,
        'nombre'=>$nombre,
        'nombre_negocio'=>$nombre_negocio,
        'direccion'=>$direccion,
        'direccion_cobro'=>$direccion_cobro,
        'telf'=>$telf,
        'email'=>$email,
        'referencia_1'=>$referencia_1,
        'referencia_2'=>$referencia_2);
       $this->db->where('id', $id_cliente);
       $this->db->update('t_cliente', $data);
    }
    public function get_cliente_id($id_cliente){
    	$this->db->select('t_cliente.id as id_cliente, t_tipo_estado_cliente.descripcion as estado_cliente, t_reputacion.descripcion as reputacion_cliente, t_cobrador.nombre as nombre_cobrador, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_documentacion_cliente.descripcion as documentacion_cliente, t_cliente.nombre_negocio as nombre_negocio_cliente, t_cliente.direccion as direccion_cliente, t_cliente.direccion_cobro as direccion_cobro_cliente, t_cliente.telf as telf_cliente, t_cliente.email as email_cliente, t_cliente.referencia_1 as referencia_1_cliente, t_cliente.referencia_2 as referencia_2_cliente, t_cliente.adjunto as adjunto_cliente');
    	$this->db->join('t_tipo_estado_cliente', 't_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id', 'left');
    	$this->db->join('t_reputacion', 't_cliente.id_reputacion = t_reputacion.id', 'left');
    	$this->db->join('t_cobrador', 't_cliente.id_cobrador = t_cobrador.id', 'left');
        $this->db->join('t_documentacion_cliente', 't_cliente.id_documentacion = t_documentacion_cliente.id', 'left');
    	$this->db->where('t_cliente.id', $id_cliente);
    	$consulta=$this->db->get('t_cliente',1);
    	  if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function get_cliente_id_cobrador($id_cobrador){
        $this->db->select('t_cliente.id as id_cliente, t_tipo_estado_cliente.descripcion as estado_cliente, t_reputacion.descripcion as reputacion_cliente, t_cobrador.nombre as nombre_cobrador, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_documentacion_cliente.descripcion as documentacion_cliente, t_cliente.nombre_negocio as nombre_negocio_cliente, t_cliente.direccion as direccion_cliente, t_cliente.direccion_cobro as direccion_cobro_cliente, t_cliente.telf as telf_cliente, t_cliente.email as email_cliente, t_cliente.referencia_1 as referencia_1_cliente, t_cliente.referencia_2 as referencia_2_cliente, t_cliente.adjunto as adjunto_cliente');
        $this->db->join('t_tipo_estado_cliente', 't_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id', 'left');
        $this->db->join('t_reputacion', 't_cliente.id_reputacion = t_reputacion.id', 'left');
        $this->db->join('t_cobrador', 't_cliente.id_cobrador = t_cobrador.id', 'left');
        $this->db->join('t_documentacion_cliente', 't_cliente.id_documentacion = t_documentacion_cliente.id', 'left');
        $this->db->where('t_cliente.id_cobrador', $id_cobrador);
        $consulta=$this->db->get('t_cliente');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function get_cliente_prestamo(){
      $this->db->select('t_cliente.id as id_cliente, t_tipo_estado_cliente.descripcion as estado_cliente, t_reputacion.descripcion as reputacion_cliente, t_cobrador.nombre as nombre_cobrador, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_cliente.nombre_negocio as nombre_negocio_cliente, t_cliente.direccion as direccion_cliente, t_cliente.direccion_cobro as direccion_cobro_cliente, t_cliente.telf as telf_cliente, t_cliente.email as email_cliente, t_cliente.referencia_1 as referencia_1_cliente, t_cliente.referencia_2 as referencia_2_cliente, t_cliente.adjunto as adjunto_cliente');
      $this->db->join('t_tipo_estado_cliente', 't_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id', 'left');
      $this->db->join('t_reputacion', 't_cliente.id_reputacion = t_reputacion.id', 'left');
      $this->db->join('t_cobrador', 't_cliente.id_cobrador = t_cobrador.id', 'left');
      $consulta=$this->db->get('t_cliente');
        if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function get_cliente_prestamo_cobrador($id_cobrador){
      $this->db->select('t_cliente.id as id_cliente, t_tipo_estado_cliente.descripcion as estado_cliente, t_reputacion.descripcion as reputacion_cliente, t_cobrador.nombre as nombre_cobrador, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_cliente.nombre_negocio as nombre_negocio_cliente, t_cliente.direccion as direccion_cliente, t_cliente.direccion_cobro as direccion_cobro_cliente, t_cliente.telf as telf_cliente, t_cliente.email as email_cliente, t_cliente.referencia_1 as referencia_1_cliente, t_cliente.referencia_2 as referencia_2_cliente, t_cliente.adjunto as adjunto_cliente');
      $this->db->where('t_cliente.id_cobrador', $id_cobrador);
      $this->db->join('t_tipo_estado_cliente', 't_cliente.id_tipo_estado_cliente = t_tipo_estado_cliente.id', 'left');
      $this->db->join('t_reputacion', 't_cliente.id_reputacion = t_reputacion.id', 'left');
      $this->db->join('t_cobrador', 't_cliente.id_cobrador = t_cobrador.id', 'left');
      $consulta=$this->db->get('t_cliente');
        if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function get_cliente_dinero_sucursal($id_cliente){
        $this->db->select('t_cliente.id as id_cliente,t_zona_cobrador.id_sucursal as id_sucursal, t_caja.total_caja as total_caja, t_caja.id as id_caja,  t_cobrador.nombre as nombre_cobrador');
        $this->db->join('t_cobrador', 't_cliente.id_cobrador = t_cobrador.id', 'left');
        $this->db->join('t_zona_cobrador', 't_cobrador.id = t_zona_cobrador.id_cobrador', 'left');
        $this->db->join('t_sucursal', 't_zona_cobrador.id_sucursal = t_sucursal.id', 'left');
        $this->db->join('t_caja', 't_sucursal.id = t_caja.id_sucursal', 'left');
        $this->db->where('t_cliente.id', $id_cliente);
        $consulta=$this->db->get('t_cliente',1);
        if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function actualizar_estado_cliente($id_cliente, $id_tipo_estado_cliente){
    	$data = array('id_tipo_estado_cliente' =>$id_tipo_estado_cliente);
    	$this->db->where('id', $id_cliente);
    	$this->db->update('t_cliente', $data);
    }
    public function actualizar_cobrador_cliente($id_cliente, $id_cobrador){
    	$data = array('id_cobrador' =>$id_cobrador);
    	$this->db->where('id', $id_cliente);
    	$this->db->update('t_cliente', $data);
    }
    public function actualizar_reputacion_cliente($id_cliente, $id_reputacion){
    	$data = array('id_reputacion' =>$id_reputacion);
    	$this->db->where('id', $id_cliente);
    	$this->db->update('t_cliente', $data);
    }
    public function actualizar_documentacion_cliente($id_cliente, $id_documentacion){
        $data = array('id_documentacion' =>$id_documentacion);
        $this->db->where('id', $id_cliente);
        $this->db->update('t_cliente', $data);
    }
    public function get_cliente(){
        $consulta=$this->db->get('t_cliente');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function contar_cliente(){
            $this->db->from('t_cliente');
            return $this->db->count_all_results();
    }
    public function contar_cliente_x_cobrador($id_cobrador){
        $this->db->where('id_cobrador', $id_cobrador);
            $this->db->from('t_cliente');
            return $this->db->count_all_results();
    }
}